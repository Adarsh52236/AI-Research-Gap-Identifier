"""Test API papers download."""
from fastapi.testclient import TestClient
from unittest.mock import patch
from backend.app.main import app
from backend.app.db.schemas import DownloadPaperResponse

client = TestClient(app)

@patch("backend.app.api.v1.papers.downloader.download_pdf")
def test_api_download_paper(mock_download_pdf):
    mock_download_pdf.return_value = DownloadPaperResponse(
        status="downloaded",
        paper_id="abc",
        source="arxiv",
        local_path="storage/downloads/arxiv/2024/abc.pdf",
        sha256="fakehash",
        size_bytes=1000,
        content_type="application/pdf"
    )
    
    response = client.post("/api/v1/papers/download/", json={
        "pdf_url": "https://example.com/test.pdf",
        "paper_id": "abc",
        "source": "arxiv",
        "year": 2024
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "downloaded"
    assert data["paper_id"] == "abc"
    assert data["local_path"] == "storage/downloads/arxiv/2024/abc.pdf"
