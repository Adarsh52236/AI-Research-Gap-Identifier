from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "AI Research Gap Identifier API",
        "version": "0.1.0"
    }
