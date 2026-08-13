"""Tests for gap report validator."""
from backend.app.db.schemas import GapReport, GapCandidate
from backend.app.core.gap_analyzer.gap_validator import validate_gap_report

def test_validate_gap_report():
    candidate = GapCandidate(
        gap_id="1", title="test", summary="sum", why_it_is_a_gap="why",
        proposed_research_questions=[], suggested_methodology=[],
        suggested_evaluation=[], risks_and_limitations=[],
        citations=["sig_123"], confidence=0.9
    )
    
    report = GapReport(
        status="ok", query="q", created_at="2024", model="llama",
        paper_ids=[], gaps=[candidate]
    )
    
    # Valid
    assert len(validate_gap_report(report, {"sig_123", "vec_1"})) == 0
    
    # Invalid citation
    assert len(validate_gap_report(report, {"sig_999"})) == 1
    
    # Empty citations
    candidate.citations = []
    assert len(validate_gap_report(report, {"sig_123"})) == 1
    
    # Invalid confidence
    candidate.citations = ["sig_123"]
    candidate.confidence = 1.5
    assert len(validate_gap_report(report, {"sig_123"})) == 1
