"""Gap analysis endpoints."""
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks, UploadFile, File, Depends
from backend.app.core.deps import get_current_user
from backend.app.db.models import User
from backend.app.middleware.rate_limiter import limiter
from backend.app.config import settings
from backend.app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.post("/")
async def analyze_gap():
    """Analyze gap endpoint."""
    return {"message": "Gap analysis"}

import fitz # PyMuPDF
from io import BytesIO

@router.post("/upload-user-document/")
async def upload_user_document(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    """Uploads a user document (PDF or Text), extracts text, and returns it."""
    try:
        content = await file.read()
        text = ""
        if file.filename.lower().endswith(".pdf"):
            doc = fitz.open(stream=content, filetype="pdf")
            for page in doc:
                text += page.get_text()
            doc.close()
        else:
            text = content.decode("utf-8", errors="ignore")
            
        return {"filename": file.filename, "extracted_text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")

from backend.app.db.schemas import MineGapSignalsRequest, MineGapSignalsResponse
from backend.app.core.gap_analyzer.gap_signal_service import GapSignalService

gap_service = GapSignalService()

@router.post("/gap-signals/", response_model=MineGapSignalsResponse)
async def mine_gap_signals(request: MineGapSignalsRequest):
    """Mine deterministic gap signals from parsed sections."""
    if not request.paper_ids and not request.processed_sections_paths:
        raise HTTPException(status_code=400, detail="Must provide paper_ids or processed_sections_paths")
        
    return gap_service.process_mining_request(
        paper_ids=request.paper_ids,
        processed_sections_paths=request.processed_sections_paths,
        top_k=request.top_k,
        include_sections=request.include_sections,
        save=request.save
    )

from backend.app.db.schemas import IndexEmbeddingsRequest, IndexEmbeddingsResponse
from backend.app.db.schemas import SimilaritySearchRequest, SimilaritySearchResponse
from backend.app.core.embeddings.indexing_service import EmbeddingIndexingService
from backend.app.core.embeddings.similarity_search import SimilaritySearchService

indexing_service = EmbeddingIndexingService()
search_service = SimilaritySearchService()

@router.post("/index-embeddings/", response_model=IndexEmbeddingsResponse)
async def index_embeddings(request: IndexEmbeddingsRequest):
    """Index sections into ChromaDB."""
    if not request.paper_ids and not request.processed_sections_paths:
        raise HTTPException(status_code=400, detail="Must provide paper_ids or paths")
        
    sections = request.sections
    if not sections:
        sections = [s.strip() for s in settings.INDEX_SECTIONS_DEFAULT.split(",")]
        
    return indexing_service.index_paper_ids(
        paper_ids=request.paper_ids,
        processed_sections_paths=request.processed_sections_paths,
        sections_to_index=sections,
        force_reindex=request.force_reindex,
        save_text=request.save_text
    )

@router.post("/similarity-search/", response_model=SimilaritySearchResponse)
async def similarity_search(request: SimilaritySearchRequest):
    """Search ChromaDB using semantic similarity."""
    return search_service.search(
        query_text=request.query_text,
        top_k=request.top_k,
        filter_source=request.filter_source,
        filter_year_from=request.filter_year_from,
        filter_year_to=request.filter_year_to,
        filter_section=request.filter_section
    )

from backend.app.db.schemas import GapReportRequest, GapReportResponse
from backend.app.core.gap_analyzer.gap_report_service import GapReportService

gap_report_service = GapReportService()

@router.post("/gap-report/", response_model=GapReportResponse)
@limiter.limit(settings.RATE_LIMIT_REPORT)
async def generate_gap_report(request: Request, report_request: GapReportRequest):
    """
    Synthesize an LLM-based gap report from vector search excerpts and mined gap signals.
    """
    try:
        return await gap_report_service.generate_report(report_request)
    except Exception as e:
        logger.error(f"Gap report generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

from backend.app.db.schemas import PipelineRunRequest, PipelineRunStatus
from backend.app.core.pipeline.pipeline_runner import PipelineRunner
from backend.app.core.pipeline.pipeline_runner import PipelineRunner
from backend.app.core.pipeline.run_store import get_run_store
import os

pipeline_runner = PipelineRunner()
run_store = get_run_store()

@router.post("/pipeline-run/", response_model=PipelineRunStatus)
@limiter.limit(settings.RATE_LIMIT_PIPELINE)
async def run_pipeline(request: Request, run_request: PipelineRunRequest, background_tasks: BackgroundTasks, async_run: bool | None = None, current_user: User = Depends(get_current_user)):
    """
    Executes a multi-paper batch pipeline.
    """
    try:
        if async_run is None:
            async_run = settings.ENVIRONMENT == "production"
            
        if async_run:
            import uuid
            run_id = str(uuid.uuid4())
            run_request.run_id = run_id
            
            initial_status = PipelineRunStatus(
                run_id=run_id,
                user_id=current_user.id,
                status="pending",
                steps=run_request.steps,
                query=run_request.query,
                started_at=__import__('datetime').datetime.utcnow().isoformat()
            )
            # Create in store immediately so frontend sees it
            run_store.create_run(initial_status)
            
            # Fire and forget
            background_tasks.add_task(pipeline_runner.run, run_request, user_id=current_user.id)
            
            return initial_status
        else:
            # For synchronous execution, the user_id isn't directly passed to run_request yet because run_request is PipelineRunRequest, but the runner creates the status.
            # We'll attach it so PipelineRunner can read it, or we'll update the runner next.
            return await pipeline_runner.run(run_request, user_id=current_user.id)
    except Exception as e:
        logger.error(f"Pipeline run failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pipeline-run/{run_id}", response_model=PipelineRunStatus)
def get_pipeline_run(run_id: str, current_user: User = Depends(get_current_user)):
    """
    Get the status of a pipeline run.
    """
    status = run_store.get_run(run_id)
    if not status:
        raise HTTPException(status_code=404, detail="Run ID not found")
    return status

@router.get("/pipeline-run/{run_id}/report")
def get_pipeline_run_report(run_id: str, current_user: User = Depends(get_current_user)):
    """
    Get the generated report content for a pipeline run.
    """
    status = run_store.get_run(run_id)
    if not status:
        raise HTTPException(status_code=404, detail="Run ID not found")
        
    if not status.report_path:
        raise HTTPException(status_code=404, detail="Report not generated")
        
    # Check if report is remote (Supabase storage URL)
    if status.report_path.startswith("http://") or status.report_path.startswith("https://"):
        import requests
        resp = requests.get(status.report_path)
        if resp.status_code == 200:
            return {"report_path": status.report_path, "content": resp.text}
        else:
            raise HTTPException(status_code=404, detail="Remote report not found")
            
    # Fallback to local
    if not os.path.exists(status.report_path):
        raise HTTPException(status_code=404, detail="Report not found")
        
    with open(status.report_path, "r", encoding="utf-8") as f:
        return {"report_path": status.report_path, "content": f.read()}

from typing import List

@router.get("/runs", response_model=List[PipelineRunStatus])
def list_recent_runs(limit: int = 50, current_user: User = Depends(get_current_user)):
    """List recent pipeline runs."""
    return run_store.list_runs(limit=limit, user_id=current_user.id)

@router.delete("/runs/{run_id}")
def delete_pipeline_run(run_id: str, current_user: User = Depends(get_current_user)):
    """Delete a specific pipeline run."""
    status = run_store.get_run(run_id)
    if not status:
        raise HTTPException(status_code=404, detail="Run not found")
    if status.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this run")
        
    deleted = run_store.delete_run(run_id)
    if not deleted:
        raise HTTPException(status_code=500, detail="Failed to delete run")
    return {"message": "Run deleted successfully"}

@router.delete("/runs")
def clear_pipeline_runs(current_user: User = Depends(get_current_user)):
    """Clear all pipeline runs for the current user."""
    deleted_count = run_store.delete_all_runs(user_id=current_user.id)
    return {"message": f"Successfully deleted {deleted_count} runs", "deleted_count": deleted_count}
