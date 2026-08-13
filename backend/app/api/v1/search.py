"""Paper search endpoints."""
from fastapi import APIRouter, HTTPException
from backend.app.db.schemas import SearchRequest, SearchResponse
from backend.app.core.fetcher.fetcher_manager import FetcherManager
from backend.app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)
fetcher_manager = FetcherManager()

@router.post("/", response_model=SearchResponse)
async def search_papers(request: SearchRequest):
    """Search papers endpoint."""
    try:
        results = await fetcher_manager.search_all(
            query=request.query,
            limit=request.limit,
            sources=request.sources,
            year_from=request.year_from,
            year_to=request.year_to
        )
        return SearchResponse(
            query=request.query,
            count=len(results),
            results=results
        )
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail="Search failed")
