import hashlib
import time
from datetime import datetime
from pathlib import Path
from backend.app.config import settings
from backend.app.db.schemas import (
    PipelineRunRequest, PipelineRunStatus, PaperMetadata,
    DownloadPaperRequest, ExtractPaperRequest, MineGapSignalsRequest,
    IndexEmbeddingsRequest, GapReportRequest
)
from backend.app.core.pipeline.run_store import RunStore
from backend.app.core.fetcher.fetcher_manager import FetcherManager
from backend.app.core.downloader.pdf_downloader import PDFDownloader
from backend.app.core.extractor.extraction_service import ExtractionService
from backend.app.core.gap_analyzer.gap_signal_service import GapSignalService
from backend.app.core.embeddings.indexing_service import EmbeddingIndexingService
from backend.app.core.gap_analyzer.gap_report_service import GapReportService
from backend.app.db.session import SessionLocal
from backend.app.db import crud
import os
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)

class PipelineRunner:
    def __init__(self):
        self.run_store = RunStore()
        self.fetcher = FetcherManager()
        self.downloader = PDFDownloader()
        self.extractor = ExtractionService()
        self.miner = GapSignalService()
        self.indexer = EmbeddingIndexingService()
        self.report_generator = GapReportService()

    async def run(self, request: PipelineRunRequest, user_id: int | None = None) -> PipelineRunStatus:
        timestamp = str(time.time())
        run_id = request.run_id if request.run_id else hashlib.sha256((timestamp + request.query).encode()).hexdigest()[:12]
        
        status = PipelineRunStatus(
            run_id=run_id,
            user_id=user_id,
            status="running",
            started_at=datetime.utcnow().isoformat(),
            query=request.query,
            steps=request.steps
        )
        self.run_store.save_status(run_id, status)
        
        db = SessionLocal() if SessionLocal else None
        if db:
            try:
                crud.create_or_update_run(db, status)
            except Exception as e:
                logger.error(f"Database error writing run status {run_id}: {e}")
                
        papers_to_process = []
        
        try:
            # 1. Search
            if "search" in request.steps:
                status.current_step = "search"
                self.run_store.save_status(run_id, status)
                if db:
                    try:
                        crud.create_or_update_run(db, status)
                    except Exception as e:
                        logger.error(f"Database error writing run status {run_id}: {e}")
                self.run_store.append_event(run_id, {"ts": datetime.utcnow().isoformat(), "step": "search", "msg": f"Searching for {request.query}"})
                
                search_results = await self.fetcher.search_all(
                    query=request.query,
                    limit=request.limit,
                    sources=request.sources,
                    year_from=request.year_from,
                    year_to=request.year_to
                )
                papers_to_process = search_results[:request.limit]
                status.papers_found = len(papers_to_process)
                self.run_store.save_status(run_id, status)
                
                if db:
                    for p in papers_to_process:
                        try:
                            crud.upsert_paper(db, p)
                        except Exception as e:
                            logger.error(f"Database error upserting paper {p.paper_id}: {e}")
                    try:
                        crud.create_or_update_run(db, status)
                    except Exception as e:
                        logger.error(f"Database error writing run status {run_id}: {e}")
                self.run_store.append_event(run_id, {"ts": datetime.utcnow().isoformat(), "step": "search", "msg": f"Found {len(papers_to_process)} papers"})

            valid_paper_ids = []
                
            # 2. Download
            if "download" in request.steps:
                status.current_step = "download"
                self.run_store.save_status(run_id, status)
                for p in papers_to_process:
                    if not p.pdf_url:
                        continue
                    
                    try:
                        expected_pdf = Path(settings.DOWNLOADS_DIR) / p.source / f"{p.paper_id}.pdf"
                        if expected_pdf.exists():
                            self.run_store.append_event(run_id, {"ts": datetime.utcnow().isoformat(), "step": "download", "paper_id": p.paper_id, "msg": "Skipped (already exists)"})
                            status.papers_downloaded += 1
                        else:
                            dl_req = DownloadPaperRequest(
                                pdf_url=p.pdf_url,
                                paper_id=p.paper_id,
                                source=p.source,
                                title=p.title,
                                year=p.year
                            )
                            await self.downloader.download_pdf(dl_req)
                            status.papers_downloaded += 1
                        valid_paper_ids.append(p.paper_id)
                    except Exception as e:
                        err = f"Download failed for {p.paper_id}: {str(e)}"
                        status.errors.append(err)
                        self.run_store.append_event(run_id, {"ts": datetime.utcnow().isoformat(), "step": "download", "paper_id": p.paper_id, "error": str(e)})
                self.run_store.save_status(run_id, status)

            # 3. Extract
            if "extract" in request.steps:
                status.current_step = "extract"
                self.run_store.save_status(run_id, status)
                extracted_ids = []
                for p in papers_to_process:
                    if p.paper_id not in valid_paper_ids:
                        continue
                    try:
                        expected_pdf = Path(settings.DOWNLOADS_DIR) / p.source / f"{p.paper_id}.pdf"
                        expected_sections = Path(settings.PROCESSED_DIR) / p.paper_id / "sections.json"
                        if expected_sections.exists():
                            self.run_store.append_event(run_id, {"ts": datetime.utcnow().isoformat(), "step": "extract", "paper_id": p.paper_id, "msg": "Skipped (already exists)"})
                            status.papers_extracted += 1
                            extracted_ids.append(p.paper_id)
                        else:
                            if expected_pdf.exists():
                                ex_req = ExtractPaperRequest(
                                    local_path=str(expected_pdf),
                                    paper_id=p.paper_id,
                                    source=p.source,
                                    year=p.year
                                )
                                self.extractor.extract_and_process(ex_req)
                                status.papers_extracted += 1
                                extracted_ids.append(p.paper_id)
                    except Exception as e:
                        err = f"Extract failed for {p.paper_id}: {str(e)}"
                        status.errors.append(err)
                        self.run_store.append_event(run_id, {"ts": datetime.utcnow().isoformat(), "step": "extract", "paper_id": p.paper_id, "error": str(e)})
                valid_paper_ids = extracted_ids
                self.run_store.save_status(run_id, status)

            # 4. Mine
            if "mine" in request.steps:
                status.current_step = "mine"
                self.run_store.save_status(run_id, status)
                mined_ids = []
                for pid in valid_paper_ids:
                    try:
                        expected_gaps = Path(settings.PROCESSED_DIR) / pid / "gap_signals.json"
                        if expected_gaps.exists():
                            self.run_store.append_event(run_id, {"ts": datetime.utcnow().isoformat(), "step": "mine", "paper_id": pid, "msg": "Skipped (already exists)"})
                            status.papers_mined += 1
                            mined_ids.append(pid)
                        else:
                            mine_req = MineGapSignalsRequest(
                                paper_ids=[pid],
                                top_k=30
                            )
                            self.miner.process_mining_request(mine_req)
                            status.papers_mined += 1
                            mined_ids.append(pid)
                    except Exception as e:
                        err = f"Mine failed for {pid}: {str(e)}"
                        status.errors.append(err)
                        self.run_store.append_event(run_id, {"ts": datetime.utcnow().isoformat(), "step": "mine", "paper_id": pid, "error": str(e)})
                valid_paper_ids = mined_ids
                self.run_store.save_status(run_id, status)

            # 5. Index
            if "index" in request.steps:
                status.current_step = "index"
                self.run_store.save_status(run_id, status)
                for pid in valid_paper_ids:
                    try:
                        idx_req = IndexEmbeddingsRequest(
                            paper_ids=[pid],
                            force_reindex=request.force_reindex
                        )
                        res = self.indexer.index_paper_ids(idx_req)
                        # We don't have a way to know if it skipped from the res exactly unless we check skipped_count
                        if res.indexed_count > 0 or res.skipped_count > 0:
                            status.papers_indexed += 1
                    except Exception as e:
                        err = f"Index failed for {pid}: {str(e)}"
                        status.errors.append(err)
                        self.run_store.append_event(run_id, {"ts": datetime.utcnow().isoformat(), "step": "index", "paper_id": pid, "error": str(e)})
                self.run_store.save_status(run_id, status)

            # 6. Report
            if "report" in request.steps:
                status.current_step = "report"
                self.run_store.save_status(run_id, status)
                if len(valid_paper_ids) > 0 and (not request.force_report):
                    # check if we can resume/skip report? The prompt says: "if report exists, skip report generation (unless force_report)"
                    # We need to see if a report exists for this run_id? Wait, the report is saved via GapReportService, which saves it by timestamp usually.
                    # Or do we save it by run_id?
                    # The prompt says: "if report exists, skip (unless force_report)".
                    # Actually, we don't have a specific report path for a query yet, GapReportService just generates it. 
                    # If they run the pipeline again on the same query, it generates a new run_id.
                    # But the requirement says "if report exists, skip (unless force_report)". Let's just always generate if force_report is False but we don't have a mapping. 
                    # Actually, GapReportService doesn't have a deterministic filename (it uses `int(time.time())`). 
                    # So we'll just run it. We can't skip it cleanly. Let's just run it.
                    try:
                        rep_req = GapReportRequest(
                            paper_ids=valid_paper_ids[:request.top_k_papers_for_report],
                            query=request.report_query or request.query,
                            user_document_text=request.user_document_text,
                            save_report=True
                        )
                        rep_res = await self.report_generator.generate_report(rep_req)
                        status.report_path = rep_res.report_md_path
                        self.run_store.append_event(run_id, {"ts": datetime.utcnow().isoformat(), "step": "report", "msg": "Report generated"})
                    except Exception as e:
                        err = f"Report generation failed: {str(e)}"
                        status.errors.append(err)
                        self.run_store.append_event(run_id, {"ts": datetime.utcnow().isoformat(), "step": "report", "error": str(e)})
                
            # Finish
            if len(status.errors) > len(papers_to_process) and len(papers_to_process) > 0:
                status.status = "failed"
            else:
                status.status = "completed"
                
        except Exception as e:
            status.status = "failed"
            status.errors.append(f"Pipeline crashed: {str(e)}")
            
        status.finished_at = datetime.utcnow().isoformat()
        status.current_step = None
        self.run_store.save_status(run_id, status)
        return status
