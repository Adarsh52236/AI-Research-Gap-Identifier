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
from backend.app.core.pipeline.run_store import get_run_store
from backend.app.core.fetcher.fetcher_manager import FetcherManager
from backend.app.core.downloader.pdf_downloader import PDFDownloader
from backend.app.core.extractor.extraction_service import ExtractionService
from backend.app.core.gap_analyzer.gap_signal_service import GapSignalService
from backend.app.core.embeddings.indexing_service import EmbeddingIndexingService
from backend.app.core.gap_analyzer.gap_report_service import GapReportService
from backend.app.core.gap_analyzer.groq_client import GroqLLMClient
from backend.app.core.storage.artifact_store import get_artifact_store
from backend.app.db.session import SessionLocal
from backend.app.db import crud
import os
from backend.app.utils.logger import get_logger
from backend.app.utils.file_utils import safe_filename

logger = get_logger(__name__)

class PipelineRunner:
    def __init__(self):
        self.run_store = get_run_store()
        self.fetcher = FetcherManager()
        self.downloader = PDFDownloader()
        self.extractor = ExtractionService()
        self.miner = GapSignalService()
        self.indexer = EmbeddingIndexingService()
        self.report_generator = GapReportService()
        self.llm_client = GroqLLMClient()
        self.artifact_store = get_artifact_store()

    def _update_step_status(self, run_id: str, status: PipelineRunStatus, step: str, step_state: str, error: str = None):
        if step_state in ["running", "pending"]:
            status.current_step = step
            status.step_started_at = datetime.utcnow().isoformat() + "Z"
            
        status.step_statuses[step] = step_state
        status.last_updated_at = datetime.utcnow().isoformat() + "Z"
        status.heartbeat_counter += 1
        
        if error:
            status.errors.append(f"{step} error: {error}")
            self.run_store.append_event(run_id, {"ts": datetime.utcnow().isoformat(), "step": step, "error": error})
        
        self.run_store.update_run(run_id, status)


    async def run(self, request: PipelineRunRequest, user_id: int | None = None) -> PipelineRunStatus:
        timestamp = str(time.time())
        run_id = request.run_id if request.run_id else hashlib.sha256((timestamp + request.query).encode()).hexdigest()[:12]
        
        status = PipelineRunStatus(
            run_id=run_id,
            session_id=request.session_id if request.session_id else run_id,
            user_id=user_id,
            status="running",
            started_at=datetime.utcnow().isoformat(),
            query=request.query,
            steps=request.steps
        )
        self.run_store.create_run(status)
        
        papers_to_process = []
        
        try:
            # 0. Preprocess
            self._update_step_status(run_id, status, "preprocess", "running")
            
            parsed_prompt = await self.llm_client.parse_user_prompt_json(request.query, request.user_document_text)
            
            if parsed_prompt.get("extracted_url") and not request.user_document_text:
                self.run_store.append_event(run_id, {"ts": datetime.utcnow().isoformat(), "step": "preprocess", "msg": "Extracting text from URL: " + parsed_prompt["extracted_url"]})
                dl_res = await self.downloader.download_pdf(
                    pdf_url=parsed_prompt["extracted_url"],
                    paper_id="user_url_doc",
                    source="user",
                    title="User Provided URL",
                    year=None
                )
                ex_res = self.extractor.extract_and_process(
                    local_pdf_path=Path(dl_res.local_path),
                    paper_id="user_url_doc",
                    parse_sections=False
                )
                with open(ex_res.raw_text_path, "r", encoding="utf-8") as f:
                    request.user_document_text = f.read()
                    
            # (Removed strict requirement for user_document_text to allow analysis without a base document)
            
            optimized = parsed_prompt.get("optimized_query")
            if optimized and optimized.strip():
                request.query = optimized.strip()
            
            self._update_step_status(run_id, status, "preprocess", "completed")
            
            # 1. Search
            if "search" in request.steps:
                self._update_step_status(run_id, status, "search", "running")
                if SessionLocal:
                    with SessionLocal() as db:
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
                self.run_store.update_run(run_id, status)
                
                self.run_store.append_event(run_id, {"ts": datetime.utcnow().isoformat(), "step": "search", "msg": f"Found {len(papers_to_process)} papers"})
                
                self._update_step_status(run_id, status, "search", "completed")

            valid_paper_ids = []
                
            # 2. Download
            if "download" in request.steps:
                self._update_step_status(run_id, status, "download", "running")
                for p in papers_to_process:
                    if not p.pdf_url:
                        continue
                    
                    try:
                        source_dir = safe_filename(p.source) if p.source else "unknown"
                        year_dir = str(p.year) if p.year else "unknown"
                        expected_pdf = Path(settings.DOWNLOADS_DIR) / source_dir / year_dir / f"{safe_filename(p.paper_id)}.pdf"
                        if expected_pdf.exists():
                            self.run_store.append_event(run_id, {"ts": datetime.utcnow().isoformat(), "step": "download", "paper_id": p.paper_id, "msg": "Skipped (already exists)"})
                            status.papers_downloaded += 1
                        else:
                            dl_res = await self.downloader.download_pdf(
                                pdf_url=p.pdf_url,
                                paper_id=p.paper_id,
                                source=p.source,
                                title=p.title,
                                year=p.year
                            )
                            if settings.ARTIFACT_BACKEND.lower() == "supabase":
                                remote_path = self.artifact_store.upload_file(dl_res.local_path, "documents", f"{p.paper_id}.pdf")
                                dl_res.storage_path = remote_path
                            if SessionLocal:
                                with SessionLocal() as db:
                                    try:
                                        crud.save_download_artifact(db, dl_res)
                                    except Exception as e:
                                        logger.error(f"DB error save_download_artifact for {p.paper_id}: {e}")
                            status.papers_downloaded += 1
                        valid_paper_ids.append(p.paper_id)
                    except Exception as e:
                        err = f"Download failed for {p.paper_id}: {str(e)}"
                        status.errors.append(err)
                        self._update_step_status(run_id, status, "download", "failed", err)
                
                if status.step_statuses.get("download") != "failed":
                    self._update_step_status(run_id, status, "download", "completed")

            # 3. Extract
            if "extract" in request.steps:
                self._update_step_status(run_id, status, "extract", "running")
                extracted_ids = []
                for p in papers_to_process:
                    if p.paper_id not in valid_paper_ids:
                        continue
                    try:
                        source_dir = safe_filename(p.source) if p.source else "unknown"
                        year_dir = str(p.year) if p.year else "unknown"
                        expected_pdf = Path(settings.DOWNLOADS_DIR) / source_dir / year_dir / f"{safe_filename(p.paper_id)}.pdf"
                        expected_sections = Path(settings.PROCESSED_DIR) / p.paper_id / "sections.json"
                        if expected_sections.exists():
                            self.run_store.append_event(run_id, {"ts": datetime.utcnow().isoformat(), "step": "extract", "paper_id": p.paper_id, "msg": "Skipped (already exists)"})
                            status.papers_extracted += 1
                            extracted_ids.append(p.paper_id)
                        else:
                            if expected_pdf.exists():
                                from fastapi.concurrency import run_in_threadpool
                                ex_res = await run_in_threadpool(
                                    self.extractor.extract_and_process,
                                    local_pdf_path=expected_pdf,
                                    paper_id=p.paper_id,
                                    parse_sections=True
                                )
                                if settings.ARTIFACT_BACKEND.lower() == "supabase":
                                    remote_path = self.artifact_store.upload_file(ex_res.raw_text_path, "documents", f"{p.paper_id}_raw.txt")
                                    if ex_res.sections_path:
                                        remote_path_sec = self.artifact_store.upload_file(ex_res.sections_path, "documents", f"{p.paper_id}_sections.json")
                                        ex_res.storage_path = remote_path_sec
                                    else:
                                        ex_res.storage_path = remote_path
                                if SessionLocal:
                                    with SessionLocal() as db:
                                        try:
                                            crud.save_extraction_artifact(db, ex_res)
                                        except Exception as e:
                                            logger.error(f"DB error save_extraction_artifact for {p.paper_id}: {e}")
                                status.papers_extracted += 1
                                extracted_ids.append(p.paper_id)
                    except Exception as e:
                        err = f"Extract failed for {p.paper_id}: {str(e)}"
                        status.errors.append(err)
                        self._update_step_status(run_id, status, "extract", "failed", err)
                valid_paper_ids = extracted_ids
                
                if status.step_statuses.get("extract") != "failed":
                    self._update_step_status(run_id, status, "extract", "completed")

            # 4. Mine
            if "mine" in request.steps:
                self._update_step_status(run_id, status, "mine", "running")
                mined_ids = []
                for pid in valid_paper_ids:
                    try:
                        expected_gaps = Path(settings.PROCESSED_DIR) / pid / "gap_signals.json"
                        if expected_gaps.exists():
                            self.run_store.append_event(run_id, {"ts": datetime.utcnow().isoformat(), "step": "mine", "paper_id": pid, "msg": "Skipped (already exists)"})
                            status.papers_mined += 1
                            mined_ids.append(pid)
                        else:
                            from fastapi.concurrency import run_in_threadpool
                            await run_in_threadpool(
                                self.miner.process_mining_request,
                                paper_ids=[pid],
                                processed_sections_paths=None,
                                top_k=30,
                                include_sections=None,
                                save=request.save
                            )
                            status.papers_mined += 1
                            mined_ids.append(pid)
                    except Exception as e:
                        err = f"Mine failed for {pid}: {str(e)}"
                        status.errors.append(err)
                        self._update_step_status(run_id, status, "mine", "failed", err)
                
                valid_paper_ids = mined_ids
                
                self._update_step_status(run_id, status, "mine", "completed")

            # 5. Index
            if "index" in request.steps:
                self._update_step_status(run_id, status, "index", "running")
                for pid in valid_paper_ids:
                    try:
                        import asyncio
                        from fastapi.concurrency import run_in_threadpool
                        res = await asyncio.wait_for(run_in_threadpool(
                            self.indexer.index_paper_ids,
                            paper_ids=[pid],
                            processed_sections_paths=None,
                            sections_to_index=["ABSTRACT", "INTRODUCTION", "METHODS", "RESULTS", "DISCUSSION", "CONCLUSION"],
                            force_reindex=request.force_reindex,
                            save_text=True
                        ), timeout=settings.INDEX_STEP_MAX_SECONDS)
                        # We don't have a way to know if it skipped from the res exactly unless we check skipped_count
                        if res.indexed_count > 0 or res.skipped_count > 0:
                            status.papers_indexed += 1
                    except Exception as e:
                        import asyncio
                        if isinstance(e, asyncio.TimeoutError):
                            err = f"Index timed out for {pid} after {settings.INDEX_STEP_MAX_SECONDS}s"
                            self._update_step_status(run_id, status, "index", "failed", err)
                            break # stop indexing remaining papers
                        else:
                            err = f"Index failed for {pid}: {str(e)}"
                            self._update_step_status(run_id, status, "index", "failed", err)
                
                if status.step_statuses.get("index") != "failed":
                    self._update_step_status(run_id, status, "index", "completed")

            # 6. Report
            if "report" in request.steps:
                self._update_step_status(run_id, status, "report", "running")
                try:
                    rep_req = GapReportRequest(
                        paper_ids=valid_paper_ids[:request.top_k_papers_for_report] if hasattr(request, 'top_k_papers_for_report') else valid_paper_ids,
                        query=request.query,
                        user_document_text=request.user_document_text[:4000] if request.user_document_text else None,
                        save_report=True
                    )
                    rep_res = await self.report_generator.generate_report(rep_req)
                    if settings.ARTIFACT_BACKEND.lower() == "supabase" and rep_res.report_md_path:
                        remote_path = self.artifact_store.upload_file(rep_res.report_md_path, "documents", f"report_{run_id}.md")
                        rep_res.storage_path = remote_path
                    if SessionLocal:
                        with SessionLocal() as db:
                            try:
                                crud.save_report(db, run_id, rep_res)
                            except Exception as e:
                                logger.error(f"DB error save_report for {run_id}: {e}")
                    status.report_path = rep_res.report_md_path
                    self.run_store.append_event(run_id, {"ts": datetime.utcnow().isoformat(), "step": "report", "msg": "Report generated"})
                except Exception as e:
                    err = f"Report generation failed: {str(e)}"
                    status.errors.append(err)
                    status.status = "failed"
                    self.run_store.append_event(run_id, {"ts": datetime.utcnow().isoformat(), "step": "report", "error": str(e)})
                    self.run_store.update_run(run_id, status)
                    return status
                
            # Finish
            if len(status.errors) > len(papers_to_process) and len(papers_to_process) > 0:
                status.status = "failed"
            else:
                status.status = "completed"
                
        except Exception as e:
            status.status = "failed"
            status.errors.append(f"Pipeline crashed: {str(e)}")
        finally:
            if not status.finished_at:
                status.finished_at = datetime.utcnow().isoformat() + "Z"
            status.current_step = None
            if status.status not in ["completed", "failed"]:
                status.status = "failed" # Ensure terminal
            self.run_store.update_run(run_id, status)
            
        return status
