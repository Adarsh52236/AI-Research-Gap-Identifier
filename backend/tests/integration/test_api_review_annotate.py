import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from pathlib import Path
import pymupdf as fitz
from backend.app.main import app
from backend.app.db.schemas import ReviewLLMOutput, ReviewIssue, ReviewEvidence

client = TestClient(app)

@pytest.fixture
def sample_pdf(tmp_path):
    pdf_path = tmp_path / "test_paper.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "ABSTRACT. This is a test paper. INTRODUCTION. We propose something new.", fontsize=12)
    doc.save(str(pdf_path))
    doc.close()
    return pdf_path

def test_api_review_annotate(sample_pdf):
    # Mock LLM Client
    mock_llm = ReviewLLMOutput(
        issues=[
            ReviewIssue(
                issue_id="i1",
                severity="major",
                issue="Test issue",
                solution="Test solution",
                evidence=ReviewEvidence(
                    evidence_id="e1",
                    anchor_phrase="This is a test paper",
                    quote="This is a test paper."
                ),
                issue_type="writing"
            )
        ],
        overall_issues=["Overall 1"],
        overall_solutions=["Sol 1"]
    )
    
    with patch("backend.app.core.reviewer.reviewer_llm_client.ReviewerLLMClient.generate_review_json") as mock_gen:
        mock_gen.return_value = mock_llm
        
        with open(sample_pdf, "rb") as f:
            response = client.post(
                "/api/v1/review/annotate",
                files={"file": ("test_paper.pdf", f, "application/pdf")},
                data={"prompt": "Test"}
            )
            
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["issues_count"] == 1
        assert data["dropped_count"] == 0
        
        annotated_path = Path(data["annotated_pdf_path"])
        assert annotated_path.exists()
        assert annotated_path.name == "Research_Paper_Annotated_Issues_Solutions.pdf"
