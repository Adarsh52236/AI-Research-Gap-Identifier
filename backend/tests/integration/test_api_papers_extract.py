"""Integration test for extraction endpoint."""
import fitz
from fastapi.testclient import TestClient
from pathlib import Path
from backend.app.main import app
from backend.app.config import settings
import pytest

client = TestClient(app)

def test_api_extract_paper(tmp_path, monkeypatch):
    # Setup mock storage
    storage_dir = tmp_path / "storage"
    downloads_dir = storage_dir / "downloads" / "arxiv" / "2024"
    processed_dir = storage_dir / "processed"
    downloads_dir.mkdir(parents=True, exist_ok=True)
    
    monkeypatch.setattr(settings, "STORAGE_DIR", str(storage_dir))
    monkeypatch.setattr(settings, "PROCESSED_DIR", str(processed_dir))
    
    # Create mock PDF
    pdf_path = downloads_dir / "testpaper.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(fitz.Point(50, 50), "ABSTRACT\nMock abstract.\nINTRODUCTION\nMock intro.")
    doc.save(pdf_path)
    doc.close()
    
    # Needs to be a relative path relative to STORAGE_DIR to pass safe_resolve_under
    # Since safe_resolve_under expects relative to base_dir (STORAGE_DIR)
    rel_path = "downloads/arxiv/2024/testpaper.pdf"
    
    response = client.post("/api/v1/papers/extract/", json={
        "local_path": rel_path,
        "paper_id": "testpaper_id"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "extracted"
    assert data["paper_id"] == "testpaper_id"
    assert "ABSTRACT" in data["sections_found"]
    
    # Check artifacts
    assert Path(data["raw_text_path"]).exists()
    assert Path(data["sections_path"]).exists()
