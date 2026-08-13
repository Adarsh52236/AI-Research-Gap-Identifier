"""PDF downloader module."""
import httpx
import os
from pathlib import Path
from fastapi import HTTPException
from backend.app.config import settings
from backend.app.db.schemas import DownloadPaperResponse
from backend.app.utils.file_utils import ensure_dir, safe_filename, compute_sha256, write_stream_to_file
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)

class PDFDownloader:
    """Handles downloading and verifying PDF files."""
    
    async def download_pdf(
        self,
        pdf_url: str,
        paper_id: str,
        source: str | None,
        title: str | None,
        year: int | None,
    ) -> DownloadPaperResponse:
        
        if not pdf_url.startswith(("http://", "https://")):
            raise HTTPException(status_code=400, detail="Invalid URL scheme. Must be http or https.")
            
        source_dir = safe_filename(source) if source else "unknown"
        year_dir = str(year) if year else "unknown"
        
        base_downloads_dir = Path(settings.DOWNLOADS_DIR)
        dest_dir = base_downloads_dir / source_dir / year_dir
        ensure_dir(dest_dir)
        
        dest_filename = f"{safe_filename(paper_id)}.pdf"
        dest_path = dest_dir / dest_filename
        
        max_bytes = settings.MAX_PDF_SIZE_MB * 1024 * 1024
        
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=settings.HTTP_TIMEOUT_SECONDS) as client:
                async with client.stream("GET", pdf_url) as response:
                    if response.status_code != 200:
                        logger.error(f"Failed to fetch PDF. Status code: {response.status_code}")
                        raise HTTPException(status_code=502, detail=f"Upstream fetch failed with status {response.status_code}")
                    
                    content_type = response.headers.get("content-type", "")
                    
                    try:
                        bytes_written = await write_stream_to_file(response.aiter_bytes(), dest_path, max_bytes)
                    except ValueError as ve:
                        # Exceeded size limit
                        if dest_path.exists():
                            dest_path.unlink()
                        raise HTTPException(status_code=413, detail=str(ve))
                        
                    if bytes_written == 0:
                        if dest_path.exists():
                            dest_path.unlink()
                        raise HTTPException(status_code=400, detail="Downloaded file is empty")
                        
                    # Validate PDF magic bytes
                    is_pdf_content = False
                    with open(dest_path, "rb") as f:
                        magic_bytes = f.read(4)
                        if magic_bytes == b"%PDF":
                            is_pdf_content = True
                            
                    if not ("pdf" in content_type.lower()) and not is_pdf_content:
                        if dest_path.exists():
                            dest_path.unlink()
                        raise HTTPException(status_code=400, detail="Downloaded file does not appear to be a PDF")
                        
        except httpx.ReadTimeout:
            logger.error("Timeout fetching PDF")
            if dest_path.exists():
                dest_path.unlink()
            raise HTTPException(status_code=504, detail="Timeout fetching PDF")
        except httpx.RequestError as e:
            logger.error(f"Request error fetching PDF: {e}")
            if dest_path.exists():
                dest_path.unlink()
            raise HTTPException(status_code=502, detail="Upstream fetch failed")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error downloading PDF: {e}")
            if dest_path.exists():
                dest_path.unlink()
            raise HTTPException(status_code=500, detail="Internal server error during download")
            
        sha256 = compute_sha256(dest_path)
        
        # Use relative path as requested (e.g. storage/downloads/...)
        local_path = dest_path.as_posix()
        
        return DownloadPaperResponse(
            status="downloaded",
            paper_id=paper_id,
            source=source,
            local_path=local_path,
            sha256=sha256,
            size_bytes=bytes_written,
            content_type=content_type
        )
