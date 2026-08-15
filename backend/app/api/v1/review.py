import uuid
import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from backend.app.config import settings
from backend.app.db.schemas import ReviewAnnotateRequest, ReviewAnnotateResponse
from backend.app.core.reviewer.review_service import ReviewService

router = APIRouter()
review_service = ReviewService()

@router.post("/annotate", response_model=ReviewAnnotateResponse)
async def annotate_review(
    file: UploadFile = File(...),
    prompt: str | None = Form(None),
    annotations_target: int = Form(12),
    style_guide: str | None = Form(None)
):
    if not file.filename.lower().endswith(".pdf"):
        # "For DOCX/image: implement “best-effort” with clear behavior: If not available, return HTTP 400"
        raise HTTPException(status_code=400, detail="Currently, only PDF files are supported for peer-review annotation.")
        
    run_id = str(uuid.uuid4())
    
    upload_dir = Path(settings.UPLOADS_DIR) / run_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / file.filename
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    req = ReviewAnnotateRequest(
        prompt=prompt,
        annotations_target=annotations_target,
        style_guide=style_guide
    )
    
    try:
        response = await review_service.generate_annotated_review(file_path, req, run_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{review_run_id}")
async def download_annotated_pdf(review_run_id: str):
    file_path = Path(settings.REVIEW_REPORTS_DIR) / review_run_id / "Research_Paper_Annotated_Issues_Solutions.pdf"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Annotated PDF not found.")
        
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename="Research_Paper_Annotated_Issues_Solutions.pdf"
    )
