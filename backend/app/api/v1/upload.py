"""File upload endpoints."""
from fastapi import APIRouter, UploadFile, File

router = APIRouter()

@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    """File upload endpoint."""
    return {"filename": file.filename}
