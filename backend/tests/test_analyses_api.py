import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.base import Base
from app.database.database import get_db
from app.models.project import Project
from app.core.enums import AnalysisStatus

# Reusing mock from previous test logic
from app.api.endpoints.analysis import get_research_analysis_service
from tests.test_analysis_persistence import MockResearchAnalysisService

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_analyses_api.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

def override_get_research_analysis_service():
    return MockResearchAnalysisService(should_fail=False)

from app.api.deps import get_current_user_dep
from app.models.user import User

import uuid
mock_user_id = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")

def override_get_current_user():
    return User(id=mock_user_id, email="test@example.com", username="testuser")



client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_research_analysis_service] = override_get_research_analysis_service
    app.dependency_overrides[get_current_user_dep] = override_get_current_user
    yield
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()

@pytest.fixture
def project():
    db = TestingSessionLocal()
    p = Project(name="API Test Project " + str(uuid4()), user_id=mock_user_id)
    db.add(p)
    db.commit()
    db.refresh(p)
    db.close()
    return p

def test_create_analysis(project):
    response = client.post(
        f"/api/v1/projects/{project.id}/analyses?query=Deep Learning&max_results=5"
    )
    assert response.status_code == 201
    data = response.json()
    assert data["query"] == "Deep Learning"
    assert data["status"] == AnalysisStatus.COMPLETED.value
    assert data["paper_count"] == 10  # from mock
    assert "id" in data

def test_create_analysis_project_not_found():
    fake_id = str(uuid4())
    response = client.post(
        f"/api/v1/projects/{fake_id}/analyses?query=Deep Learning"
    )
    assert response.status_code == 404

def test_list_analyses(project):
    # Create two
    client.post(f"/api/v1/projects/{project.id}/analyses?query=Q1")
    client.post(f"/api/v1/projects/{project.id}/analyses?query=Q2")
    
    response = client.get(f"/api/v1/projects/{project.id}/analyses")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert "query" in data[0]
    assert "raw_response" not in data[0] # ListItem doesn't have it

def test_get_analysis(project):
    create_res = client.post(f"/api/v1/projects/{project.id}/analyses?query=Q1")
    analysis_id = create_res.json()["id"]
    
    get_res = client.get(f"/api/v1/analyses/{analysis_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == analysis_id
    assert "raw_response" in get_res.json()

def test_delete_analysis(project):
    create_res = client.post(f"/api/v1/projects/{project.id}/analyses?query=Delete Me")
    analysis_id = create_res.json()["id"]
    
    del_res = client.delete(f"/api/v1/analyses/{analysis_id}")
    assert del_res.status_code == 204
    
    # Should be hidden from GET
    get_res = client.get(f"/api/v1/analyses/{analysis_id}")
    assert get_res.status_code == 404
    
    # Should be hidden from List
    list_res = client.get(f"/api/v1/projects/{project.id}/analyses")
    assert len(list_res.json()) == 0
