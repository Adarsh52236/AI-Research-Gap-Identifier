"""Paper search endpoints."""
from fastapi import APIRouter, HTTPException, Request
from backend.app.db.schemas import SearchRequest, SearchResponse
from backend.app.core.fetcher.fetcher_manager import FetcherManager
from backend.app.utils.logger import get_logger
from backend.app.middleware.rate_limiter import limiter
from backend.app.config import settings

router = APIRouter()
logger = get_logger(__name__)
fetcher_manager = FetcherManager()

@router.post("/", response_model=SearchResponse)
@limiter.limit(settings.RATE_LIMIT_SEARCH)
async def search_papers(request: Request, search_request: SearchRequest):
    """Search papers endpoint."""
    try:
        results = await fetcher_manager.search_all(
            query=search_request.query,
            limit=search_request.limit,
            sources=search_request.sources,
            year_from=search_request.year_from,
            year_to=search_request.year_to
        )
        return SearchResponse(
            query=search_request.query,
            count=len(results),
            results=results
        )
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail="Search failed")
