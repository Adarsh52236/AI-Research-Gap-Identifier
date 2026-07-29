import pytest
from unittest.mock import Mock
from datetime import datetime

from app.services.research_analysis.service import ResearchAnalysisService
from app.services.research_analysis.exceptions import ResearchAnalysisError
from app.services.gap_detection.models import GapDetectionResult, ResearchGap
from app.services.llm_reasoning.models import ResearchInsight

@pytest.fixture
def mock_dependencies():
    return {
        "paper_service": Mock(),
        "indexing_service": Mock(),
        "topic_service": Mock(),
        "gap_service": Mock(),
        "llm_service": Mock()
    }

@pytest.fixture
def service(mock_dependencies):
    return ResearchAnalysisService(**mock_dependencies)

def test_run_analysis_complete_workflow(service, mock_dependencies):
    """Verifies the complete happy path workflow and execution order."""
    # Setup mocks
    mock_paper = Mock()
    mock_paper.title = "Test Paper"
    mock_paper.abstract = "Test Abstract"
    mock_dependencies["paper_service"].search_papers.return_value = [mock_paper]
    
    mock_index_result = Mock(indexed_papers=1)
    mock_dependencies["indexing_service"].index_papers.return_value = mock_index_result
    
    mock_topic_result = Mock(topics=[Mock()])
    mock_dependencies["topic_service"].train.return_value = mock_topic_result
    
    mock_gap = Mock(spec=ResearchGap)
    mock_gap.id = "gap-1"
    mock_gap.title = "Gap 1"
    mock_gap_result = Mock(spec=GapDetectionResult, total_gaps=1, gaps=[mock_gap])
    mock_dependencies["gap_service"].detect_gaps.return_value = mock_gap_result
    
    mock_insight = Mock(spec=ResearchInsight)
    mock_dependencies["llm_service"].generate_insight.return_value = mock_insight
    
    # Execute
    result = service.run_analysis("AI alignment", max_results=5)
    
    # Verify execution order and metrics
    mock_dependencies["paper_service"].search_papers.assert_called_once_with(query="AI alignment", max_results=5)
    mock_dependencies["indexing_service"].index_papers.assert_called_once_with([mock_paper])
    mock_dependencies["topic_service"].train.assert_called_once_with(["Test Paper\nTest Abstract"])
    mock_dependencies["gap_service"].detect_gaps.assert_called_once_with(mock_topic_result)
    mock_dependencies["llm_service"].generate_insight.assert_called_once_with(mock_gap)
    
    # Verify result model properties
    assert result.query == "AI alignment"
    assert result.papers_indexed == 1
    assert result.topics == mock_topic_result
    assert result.gaps == mock_gap_result
    assert result.insights == [mock_insight]
    assert result.duration_seconds > 0
    assert result.started_at < result.completed_at

def test_run_analysis_partial_llm_failure(service, mock_dependencies):
    """Verifies partial failures in LLM reasoning do not stop analysis."""
    # Setup mocks
    mock_dependencies["paper_service"].search_papers.return_value = [Mock()]
    mock_dependencies["indexing_service"].index_papers.return_value = Mock(indexed_papers=1)
    mock_dependencies["topic_service"].train.return_value = Mock()
    
    # Two gaps detected
    mock_gap_1 = Mock(spec=ResearchGap, id="gap-1", title="Gap 1")
    mock_gap_2 = Mock(spec=ResearchGap, id="gap-2", title="Gap 2")
    mock_dependencies["gap_service"].detect_gaps.return_value = Mock(spec=GapDetectionResult, total_gaps=2, gaps=[mock_gap_1, mock_gap_2])
    
    # LLM Service succeeds on first, fails on second
    mock_insight_1 = Mock(spec=ResearchInsight)
    
    def side_effect(gap):
        if gap.id == "gap-1":
            return mock_insight_1
        else:
            raise Exception("LLM connection timeout")
            
    mock_dependencies["llm_service"].generate_insight.side_effect = side_effect
    
    # Execute
    result = service.run_analysis("AI alignment")
    
    # Verify successful completion despite partial failure
    assert len(result.insights) == 1
    assert result.insights[0] == mock_insight_1
    assert result.gaps.total_gaps == 2
    
def test_run_analysis_invalid_queries(service, mock_dependencies):
    """Verifies invalid queries (no results) raise ResearchAnalysisError."""
    # Empty search results
    mock_dependencies["paper_service"].search_papers.return_value = []
    
    with pytest.raises(ResearchAnalysisError, match="No papers found"):
        service.run_analysis("this-will-return-nothing")
        
    # Verify downstream services were not called
    mock_dependencies["indexing_service"].index_papers.assert_not_called()
