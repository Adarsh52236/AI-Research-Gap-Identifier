"""Health check endpoint."""
from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter()

@router.get("/")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "AI Research Gap Identifier API",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
