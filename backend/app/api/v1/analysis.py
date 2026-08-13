"""Gap analysis endpoints."""
from fastapi import APIRouter

router = APIRouter()

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
async def generate_gap_report(request: GapReportRequest):
    """Generate an LLM-based Gap Report from evidence."""
    return await gap_report_service.generate_report(request)
