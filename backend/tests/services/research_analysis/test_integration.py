import pytest
from unittest.mock import Mock
from app.services.research_analysis.service import ResearchAnalysisService
from app.services.topic_modeling.models import TopicModelResult, TopicInfo
from app.services.gap_detection.models import GapDetectionResult, ResearchGap
from app.services.llm_reasoning.models import ResearchInsight

def test_orchestrator_integration_workflow():
    """
    Integration-style test that mocks the service layer dependencies and ensures 
    the orchestrated flow correctly passes data boundaries.
    """
    # 1. Mocks setup
    paper_svc = Mock()
    indexing_svc = Mock()
    topic_svc = Mock()
    gap_svc = Mock()
    llm_svc = Mock()
    
    # 2. Dummy Data
    mock_paper = Mock(title="Neural Nets", abstract="Deep learning")
    paper_svc.search_papers.return_value = [mock_paper, mock_paper]
    
    indexing_svc.index_papers.return_value = Mock(indexed_papers=2)
    
    mock_topic_result = TopicModelResult(
        topics=[TopicInfo(id=0, name="DL", document_count=2)],
        assignments=[0, 0]
    )
    topic_svc.train.return_value = mock_topic_result
    
    mock_gap = Mock(spec=ResearchGap, id="gap-x", title="X Gap")
    mock_gap_result = GapDetectionResult(total_gaps=1, gaps=[mock_gap])
    gap_svc.detect_gaps.return_value = mock_gap_result
    
    mock_insight = Mock(spec=ResearchInsight, gap_id="gap-x")
    llm_svc.generate_insight.return_value = mock_insight
    
    # 3. Execution
    orchestrator = ResearchAnalysisService(
        paper_service=paper_svc,
        indexing_service=indexing_svc,
        topic_service=topic_svc,
        gap_service=gap_svc,
        llm_service=llm_svc
    )
    
    result = orchestrator.run_analysis("deep learning", 50)
    
    # 4. Assertions
    assert result.query == "deep learning"
    assert result.papers_indexed == 2
    assert result.topics == mock_topic_result
    assert result.gaps == mock_gap_result
    assert len(result.insights) == 1
    assert result.insights[0].gap_id == "gap-x"
    assert result.duration_seconds > 0.0
