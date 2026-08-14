"""Gap analysis endpoints."""
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from backend.app.middleware.rate_limiter import limiter
from backend.app.config import settings
from backend.app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.post("/")
async def analyze_gap():
    """Analyze gap endpoint."""
    return {"message": "Gap analysis"}

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
from backend.app.core.pipeline.run_store import RunStore
import os

pipeline_runner = PipelineRunner()
run_store = RunStore()

@router.post("/pipeline-run/", response_model=PipelineRunStatus)
@limiter.limit(settings.RATE_LIMIT_PIPELINE)
async def run_pipeline(request: Request, run_request: PipelineRunRequest, background_tasks: BackgroundTasks, async_run: bool = False):
    """
    Executes a multi-paper batch pipeline.
    """
    try:
        if async_run:
            import uuid
            run_id = str(uuid.uuid4())
            run_request.run_id = run_id
            
            # Fire and forget
            background_tasks.add_task(pipeline_runner.run, run_request)
            
            from backend.app.db.schemas import PipelineStepStatus
            initial_status = PipelineRunStatus(
                run_id=run_id,
                status=PipelineStepStatus.PENDING
            )
            return initial_status
        else:
            return await pipeline_runner.run(run_request)
    except Exception as e:
        logger.error(f"Pipeline run failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pipeline-run/{run_id}", response_model=PipelineRunStatus)
def get_pipeline_run(run_id: str):
    """
    Get the status of a pipeline run.
    """
    status = run_store.load_status(run_id)
    if not status:
        raise HTTPException(status_code=404, detail="Run ID not found")
    return status

@router.get("/pipeline-run/{run_id}/report")
def get_pipeline_run_report(run_id: str):
    """
    Get the generated report content for a pipeline run.
    """
    status = run_store.load_status(run_id)
    if not status:
        raise HTTPException(status_code=404, detail="Run ID not found")
        
    if not status.report_path or not os.path.exists(status.report_path):
        raise HTTPException(status_code=404, detail="Report not generated or not found")
        
    with open(status.report_path, "r", encoding="utf-8") as f:
        return {"report_path": status.report_path, "content": f.read()}
