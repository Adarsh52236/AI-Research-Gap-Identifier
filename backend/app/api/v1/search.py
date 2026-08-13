"""Paper search endpoints."""
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def search_papers():
    """Search papers endpoint."""
    return {"message": "Search papers"}
