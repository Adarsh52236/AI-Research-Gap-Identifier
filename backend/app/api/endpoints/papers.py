from typing import List
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services.paper_service import PaperService
from app.services.ingestion.models import Paper
from app.services.ingestion.exceptions import PaperFetchError, PaperParseError
from app.core.logging import logger

router = APIRouter()

class PaperSearchResponse(BaseModel):
    query: str
    count: int
    papers: List[Paper]

@router.get("/search", response_model=PaperSearchResponse)
def search_papers(
    query: str = Query(..., description="The search query string"),
    max_results: int = Query(10, ge=1, le=100, description="Maximum number of results to return")
):
    """
    Search for research papers by query string.
    """
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query parameter cannot be empty.")

    service = PaperService()
    
    try:
        papers = service.search_papers(query=query, max_results=max_results)
        return PaperSearchResponse(
            query=query,
            count=len(papers),
            papers=papers
        )
    except PaperFetchError as e:
        logger.error(f"External API failure during paper search: {e}")
        raise HTTPException(status_code=502, detail="Failed to fetch data from external paper source")
    except PaperParseError as e:
        logger.error(f"Parsing failure during paper search: {e}")
        raise HTTPException(status_code=500, detail="Failed to parse data from external paper source")
    except Exception as e:
        logger.error(f"Unexpected server error during paper search: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
