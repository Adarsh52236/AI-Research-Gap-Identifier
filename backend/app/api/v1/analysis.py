"""Gap analysis endpoints."""
from fastapi import APIRouter

router = APIRouter()

@router.post("/")
async def analyze_gap():
    """Analyze gap endpoint."""
    return {"message": "Gap analysis"}
