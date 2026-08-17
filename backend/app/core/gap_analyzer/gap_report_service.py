"""Gap Report Service."""
import json
import time
from datetime import datetime
from pathlib import Path
from fastapi import HTTPException

from backend.app.config import settings
from backend.app.db.schemas import GapReportResponse, GapReport, EvidenceItem, GapReportRequest
from backend.app.core.gap_analyzer.groq_client import GroqLLMClient
from backend.app.core.gap_analyzer.prompt_builder import build_gap_report_messages
from backend.app.core.gap_analyzer.gap_validator import validate_gap_report
from backend.app.core.embeddings.similarity_search import SimilaritySearchService
from backend.app.utils.file_utils import safe_resolve_under, ensure_dir
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)

class GapReportService:
    def __init__(self):
        self.llm_client = GroqLLMClient()
        self.search_service = SimilaritySearchService()
        
    def _truncate(self, text: str) -> str:
        if len(text) > settings.EVIDENCE_MAX_CHARS:
            return text[:settings.EVIDENCE_MAX_CHARS] + "..."
        return text
        
    def _generate_markdown(self, report: GapReport) -> str:
        md = f"# Research Gap Report\n"
        md += f"**Date:** {report.created_at}\n"
        md += f"**Model:** {report.model}\n"
        if report.query:
            md += f"**Query:** {report.query}\n"
        md += f"**Analyzed Papers:** {', '.join(report.paper_ids)}\n\n"
        
        if report.notes:
            md += f"> **Notes:** {report.notes}\n\n"
            
        if report.user_document_critique:
            md += f"## Comparison to User Document\n"
            md += f"{report.user_document_critique}\n\n"
            
        md += f"## Identified Gaps ({len(report.gaps)})\n\n"
        
        for i, gap in enumerate(report.gaps, 1):
            md += f"### {i}. {gap.title} (Confidence: {gap.confidence:.2f})\n"
            md += f"**Summary:** {gap.summary}\n\n"
            md += f"**Why it's a gap:** {gap.why_it_is_a_gap}\n\n"
            
            md += "**Proposed Research Questions:**\n"
            for rq in gap.proposed_research_questions: md += f"- {rq}\n"
            md += "\n"
            
            md += "**Suggested Methodology:**\n"
            for m in gap.suggested_methodology: md += f"- {m}\n"
            md += "\n"
            
            md += "**Citations (Evidence IDs):** " + ", ".join(gap.citations) + "\n\n"
            md += "---\n\n"
            
        return md

    async def generate_report(self, request: GapReportRequest) -> GapReportResponse:
        base_dir = Path(settings.STORAGE_DIR)
        evidence_pool = []
        evidence_ids = set()
        
        for pid in request.paper_ids:
            try:
                sig_path = safe_resolve_under(base_dir, f"processed/{pid}/gap_signals.json")
                if sig_path.exists():
                    with open(sig_path, "r", encoding="utf-8") as f:
                        signals = json.load(f)
                    
                    for sig in signals[:request.top_k_signals_per_paper]:
                        eid = f"sig_{sig['signal_id']}"
                        if eid not in evidence_ids:
                            evidence_pool.append(EvidenceItem(
                                evidence_id=eid,
                                paper_id=pid,
                                source_type="gap_signal",
                                section=sig.get("section"),
                                score=sig.get("score"),
                                text=self._truncate(sig.get("sentence", "")),
                                metadata=sig.get("evidence", {})
                            ))
                            evidence_ids.add(eid)
            except Exception as e:
                logger.warning(f"Failed to load gap signals for {pid}: {e}")
                
        if request.use_vector_search and request.query:
            try:
                res = self.search_service.search(
                    query_text=request.query,
                    top_k=request.top_k_sections_from_vector_search,
                    filter_source=None,
                    filter_year_from=None,
                    filter_year_to=None,
                    filter_section=None
                )
                for m in res.results:
                    if m.paper_id in request.paper_ids:
                        eid = f"vec_{m.id.replace(':', '_')}"
                        if eid not in evidence_ids:
                            evidence_pool.append(EvidenceItem(
                                evidence_id=eid,
                                paper_id=m.paper_id,
                                source_type="section_excerpt",
                                section=m.section,
                                score=m.score,
                                text=self._truncate(m.preview or ""),
                                metadata=m.metadata
                            ))
                            evidence_ids.add(eid)
            except Exception as e:
                logger.warning(f"Vector search failed during report generation: {e}. Proceeding with gap signals only.")
                request.use_vector_search = False
                        
        if not evidence_pool:
            raise HTTPException(status_code=404, detail="No evidence found for provided papers.")
            
        messages = build_gap_report_messages(request.query, evidence_pool, request.user_document_text)
        
        raw_json = await self.llm_client.generate_gap_report_json(messages)
        
        try:
            parsed = json.loads(raw_json)
            # Inject some static fields
            parsed["status"] = "ok"
            parsed["query"] = request.query
            parsed["created_at"] = datetime.utcnow().isoformat() + "Z"
            parsed["model"] = settings.GROQ_MODEL
            parsed["paper_ids"] = request.paper_ids
            report = GapReport(**parsed)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to parse LLM output: {e}")
            
        problems = validate_gap_report(report, evidence_ids)
        if problems:
            logger.warning(f"Gap Report Validation Issues: {problems}")
            # If citations are hallucinated, we filter them out to repair
            for gap in report.gaps:
                gap.citations = [c for c in gap.citations if c in evidence_ids]
                
        # Limit to top K
        report.gaps = report.gaps[:settings.REPORT_TOP_K_GAPS]
        
        out_json_path = None
        out_md_path = None
        
        if request.save_report:
            reports_dir = Path(settings.REPORTS_DIR)
            ensure_dir(reports_dir)
            
            ts = int(time.time())
            out_json = reports_dir / f"{ts}_gap_report.json"
            out_md = reports_dir / f"{ts}_gap_report.md"
            
            with open(out_json, "w", encoding="utf-8") as f:
                f.write(report.model_dump_json(indent=2))
                
            md_content = self._generate_markdown(report)
            with open(out_md, "w", encoding="utf-8") as f:
                f.write(md_content)
                
            out_json_path = out_json.as_posix()
            out_md_path = out_md.as_posix()
            
        return GapReportResponse(
            status="ok",
            report=report,
            report_json_path=out_json_path,
            report_md_path=out_md_path
        )
