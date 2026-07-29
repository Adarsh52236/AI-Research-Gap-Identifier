from datetime import datetime, UTC
from app.services.research_analysis.models import ResearchAnalysisResult

def test_research_analysis_result_instantiation():
    """Verify that ResearchAnalysisResult can be instantiated with dummy data."""
    now = datetime.now(UTC)
    result = ResearchAnalysisResult(
        query="test query",
        papers_indexed=10,
        topics=None,  # type: ignore
        gaps=None,    # type: ignore
        insights=[],
        started_at=now,
        completed_at=now,
        duration_seconds=1.5
    )
    assert result.query == "test query"
    assert result.papers_indexed == 10
    assert result.duration_seconds == 1.5
