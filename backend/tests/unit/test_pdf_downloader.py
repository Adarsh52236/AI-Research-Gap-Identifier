"""Test PDF Downloader."""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from backend.app.core.downloader.pdf_downloader import PDFDownloader
from backend.app.config import settings

@pytest.mark.asyncio
async def test_download_pdf_success(tmp_path, monkeypatch):
    """Test successful PDF download."""
    monkeypatch.setattr(settings, "DOWNLOADS_DIR", str(tmp_path))
    
    # Mock httpx AsyncClient
    class MockResponse:
        status_code = 200
        headers = {"content-type": "application/pdf"}
        
        async def aiter_bytes(self):
            yield b"%PDF-1.4 mock pdf content"
            
        async def __aenter__(self):
            return self
            
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    class MockClientContext:
        def stream(self, method, url):
            return MockResponse()
            
        async def __aenter__(self):
            return self
            
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
            
    with patch("httpx.AsyncClient", return_value=MockClientContext()):
        downloader = PDFDownloader()
        res = await downloader.download_pdf(
            pdf_url="http://example.com/test.pdf",
            paper_id="test_id",
            source="arxiv",
            title="Test",
            year=2024
        )
        
        assert res.status == "downloaded"
        assert res.paper_id == "test_id"
        assert res.source == "arxiv"
        
        local_path = Path(res.local_path)
        assert local_path.exists()
        assert local_path.name == "test_id.pdf"
        assert res.size_bytes > 0
        assert res.sha256 != ""

@pytest.mark.asyncio
async def test_download_pdf_too_large(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "DOWNLOADS_DIR", str(tmp_path))
    monkeypatch.setattr(settings, "MAX_PDF_SIZE_MB", 0) # Force limit to 0
    
    class MockResponse:
        status_code = 200
        headers = {"content-type": "application/pdf"}
        
        async def aiter_bytes(self):
            yield b"%PDF mock large"
            
        async def __aenter__(self):
            return self
            
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    class MockClientContext:
        def stream(self, method, url):
            return MockResponse()
            
        async def __aenter__(self):
            return self
            
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    with patch("httpx.AsyncClient", return_value=MockClientContext()):
        downloader = PDFDownloader()
        with pytest.raises(HTTPException) as exc:
            await downloader.download_pdf("http://example.com/test.pdf", "test_id", "arxiv", "Test", 2024)
            
        assert exc.value.status_code == 413
