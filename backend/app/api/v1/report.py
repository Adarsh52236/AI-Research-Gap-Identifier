"""Report generation endpoints."""
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def generate_report():
    """Generate report endpoint."""
    return {"message": "Report generation"}
