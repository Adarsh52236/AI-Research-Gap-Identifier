import pytest
from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.models.project import Project
from app.models.analysis import Analysis
from app.core.enums import AnalysisStatus
from app.repositories.analysis_repository import AnalysisRepository
from app.services.analysis_service import AnalysisService
from app.schemas.analysis import AnalysisCreate, AnalysisUpdate

# Import types for mock
from app.services.research_analysis.models import ResearchAnalysisResult
from app.services.research_analysis.exceptions import ResearchAnalysisError
from app.services.topic_modeling.models import TopicModelResult
from app.services.gap_detection.models import GapDetectionResult

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_analysis_persistence.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class MockResearchAnalysisService:
    def __init__(self, should_fail=False):
        self.should_fail = should_fail
        
    def run_analysis(self, query: str, max_results: int = 100) -> ResearchAnalysisResult:
        if self.should_fail:
            raise ResearchAnalysisError("Mock pipeline failure")
            
        return ResearchAnalysisResult(
            query=query,
            papers_indexed=10,
            topics=TopicModelResult(topics=[{"id": 1}], assignments=[]),
            gaps=GapDetectionResult(total_gaps=2, gaps=[]),
            insights=[],
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
            duration_seconds=5.0
        )

@pytest.fixture(scope="module")
def db_engine():
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def project(db_session):
    p = Project(name="Test Project " + str(uuid4()))
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)
    return p

def test_analysis_repository(db_session, project):
    repo = AnalysisRepository(db_session)
    
    # Create
    create_in = AnalysisCreate(project_id=project.id, query="Test Query")
    analysis = repo.create(create_in)
    assert analysis.id is not None
    assert analysis.status == AnalysisStatus.RUNNING
    assert analysis.query == "Test Query"
    
    # Get
    fetched = repo.get(analysis.id)
    assert fetched.id == analysis.id
    
    # Update
    update_in = AnalysisUpdate(status=AnalysisStatus.COMPLETED, paper_count=5)
    updated = repo.update(analysis, update_in)
    assert updated.status == AnalysisStatus.COMPLETED
    assert updated.paper_count == 5
    
    # List by project
    analyses = repo.list_by_project(project.id)
    assert len(analyses) == 1
    
    # Soft delete
    repo.soft_delete(analysis)
    assert repo.get(analysis.id) is None
    assert len(repo.list_by_project(project.id)) == 0

def test_analysis_service_success(db_session, project):
    mock_ai = MockResearchAnalysisService(should_fail=False)
    service = AnalysisService(db_session, ai_service=mock_ai)
    
    analysis = service.run_analysis_for_project(project.id, query="AI Research")
    
    assert analysis.status == AnalysisStatus.COMPLETED
    assert analysis.paper_count == 10
    assert analysis.topic_count == 1
    assert analysis.gap_count == 2
    assert analysis.error_message is None
    assert analysis.raw_response is not None
    assert "query" in analysis.raw_response

def test_analysis_service_failure(db_session, project):
    mock_ai = MockResearchAnalysisService(should_fail=True)
    service = AnalysisService(db_session, ai_service=mock_ai)
    
    with pytest.raises(ResearchAnalysisError):
        service.run_analysis_for_project(project.id, query="AI Research")
        
    repo = AnalysisRepository(db_session)
    analyses = repo.list_by_project(project.id)
    assert len(analyses) == 1
    analysis = analyses[0]
    
    assert analysis.status == AnalysisStatus.FAILED
    assert analysis.error_message == "Mock pipeline failure"
