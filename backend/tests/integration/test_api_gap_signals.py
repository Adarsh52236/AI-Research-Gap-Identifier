"""Integration test for gap signals endpoint."""
from fastapi.testclient import TestClient
from pathlib import Path
import json
from backend.app.main import app
from backend.app.config import settings
import pytest

client = TestClient(app)

def test_api_gap_signals(tmp_path, monkeypatch):
    storage_dir = tmp_path / "storage"
    processed_dir = storage_dir / "processed" / "paper_xyz"
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    monkeypatch.setattr(settings, "STORAGE_DIR", str(storage_dir))
    monkeypatch.setattr(settings, "PROCESSED_DIR", str(tmp_path / "storage" / "processed"))
    
    # Write mock sections.json
    sections_path = processed_dir / "sections.json"
    with open(sections_path, "w", encoding="utf-8") as f:
        json.dump({
            "FUTURE WORK": "Future work needs to address these issues in larger models.",
            "CONCLUSION": "This remains an open problem."
        }, f)
        
    response = client.post("/api/v1/analysis/gap-signals/", json={
        "paper_ids": ["paper_xyz"],
        "top_k": 10
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "mined"
    assert data["count"] > 0
    assert len(data["signals"]) == 2
    assert "results_path" in data
    assert Path(data["results_path"]).exists()
