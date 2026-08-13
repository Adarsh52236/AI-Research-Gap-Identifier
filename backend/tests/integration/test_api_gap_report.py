"""Integration test for gap report API."""
from fastapi.testclient import TestClient
from pathlib import Path
import json
import pytest
from backend.app.main import app
from backend.app.config import settings
from backend.app.core.gap_analyzer.groq_client import GroqLLMClient

client = TestClient(app)

def test_api_gap_report(tmp_path, monkeypatch):
    storage_dir = tmp_path / "storage"
    processed_dir = storage_dir / "processed" / "paper_xyz"
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    monkeypatch.setattr(settings, "STORAGE_DIR", str(storage_dir))
    monkeypatch.setattr(settings, "REPORTS_DIR", str(storage_dir / "reports"))
    
    # Write mock gap_signals
    with open(processed_dir / "gap_signals.json", "w", encoding="utf-8") as f:
        json.dump([{
            "signal_id": "abc123",
            "section": "ABSTRACT",
            "sentence": "This is a gap.",
            "pattern": "future_work"
        }], f)
        
    async def mock_generate(self, msgs):
        return json.dumps({
            "gaps": [{
                "gap_id": "gap1",
                "title": "Mock Gap",
                "summary": "Sum",
                "why_it_is_a_gap": "Why",
                "proposed_research_questions": [],
                "suggested_methodology": [],
                "suggested_evaluation": [],
                "risks_and_limitations": [],
                "citations": ["sig_abc123"],
                "confidence": 0.8
            }]
        })
        
    monkeypatch.setattr(GroqLLMClient, "generate_gap_report_json", mock_generate)
    
    response = client.post("/api/v1/analysis/gap-report/", json={
        "paper_ids": ["paper_xyz"],
        "use_vector_search": False
    })
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["report"]["gaps"]) == 1
    assert "report_json_path" in data
    assert Path(data["report_json_path"]).exists()
