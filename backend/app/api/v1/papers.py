"""Papers API endpoints."""
import hashlib
from fastapi import APIRouter, HTTPException
from backend.app.db.schemas import DownloadPaperRequest, DownloadPaperResponse
from backend.app.core.downloader.pdf_downloader import PDFDownloader
from backend.app.core.fetcher.fetcher_manager import FetcherManager
from backend.app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)
downloader = PDFDownloader()

@router.post("/download/", response_model=DownloadPaperResponse)
async def download_paper(request: DownloadPaperRequest):
    """Download a paper PDF endpoint."""
    paper_id = request.paper_id
    if not paper_id:
        if request.title:
            paper_id = FetcherManager.build_stable_paper_id(
                doi=None,
                title=request.title,
                year=request.year,
                source=request.source or "unknown"
            )
        else:
            paper_id = hashlib.sha1(request.pdf_url.encode('utf-8')).hexdigest()
            
    try:
        response = await downloader.download_pdf(
            pdf_url=request.pdf_url,
            paper_id=paper_id,
            source=request.source,
            title=request.title,
            year=request.year
        )
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in download paper endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

from backend.app.db.schemas import ExtractPaperRequest, ExtractPaperResponse
from backend.app.core.extractor.extraction_service import ExtractionService
from backend.app.utils.file_utils import safe_resolve_under
from backend.app.config import settings
from pathlib import Path

extraction_service = ExtractionService()

@router.post("/extract/", response_model=ExtractPaperResponse)
async def extract_paper(request: ExtractPaperRequest):
    """Extract and parse text from a downloaded PDF."""
    
    base_dir = Path(settings.STORAGE_DIR)
    try:
        pdf_path = safe_resolve_under(base_dir, request.local_path)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    if not pdf_path.name.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Path must point to a .pdf file")
        
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
        
    paper_id = request.paper_id or pdf_path.stem
    
    return extraction_service.extract_and_process(
        local_pdf_path=pdf_path,
        paper_id=paper_id,
        parse_sections=request.parse_sections
    )
