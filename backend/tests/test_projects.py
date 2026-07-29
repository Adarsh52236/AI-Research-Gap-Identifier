import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.base import Base
from app.database.database import get_db
from app.schemas.project import ProjectStatus

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_researchos.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield

def test_create_project():
    response = client.post("/projects", json={"name": "Test Project", "description": "Desc"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["status"] == ProjectStatus.ACTIVE.value
    assert data["favorite"] is False
    assert "id" in data

def test_create_duplicate_project():
    client.post("/projects", json={"name": "Duplicate", "description": "Desc"})
    response = client.post("/projects", json={"name": "Duplicate", "description": "Desc2"})
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]

def test_create_validation_failure():
    # Name too short
    response = client.post("/projects", json={"name": "ab"})
    assert response.status_code == 422
    
def test_update_project():
    # Create
    create_res = client.post("/projects", json={"name": "Update Me"})
    project_id = create_res.json()["id"]
    
    # Update
    update_res = client.put(f"/projects/{project_id}", json={"name": "Updated Name", "description": "New desc"})
    assert update_res.status_code == 200
    data = update_res.json()
    assert data["name"] == "Updated Name"
    assert data["description"] == "New desc"
    
def test_update_duplicate_name():
    # Create two
    client.post("/projects", json={"name": "First"})
    create_res = client.post("/projects", json={"name": "Second"})
    project_id = create_res.json()["id"]
    
    # Try updating Second to First
    update_res = client.put(f"/projects/{project_id}", json={"name": "First"})
    assert update_res.status_code == 409

def test_delete_project():
    create_res = client.post("/projects", json={"name": "Delete Me"})
    project_id = create_res.json()["id"]
    
    del_res = client.delete(f"/projects/{project_id}")
    assert del_res.status_code == 200
    
    # Verify soft delete
    get_res = client.get(f"/projects/{project_id}")
    assert get_res.status_code == 404

def test_favorite_project():
    create_res = client.post("/projects", json={"name": "Fav Me"})
    project_id = create_res.json()["id"]
    
    fav_res = client.patch(f"/projects/{project_id}/favorite?favorite=true")
    assert fav_res.status_code == 200
    assert fav_res.json()["favorite"] is True
    
    # Unfavorite
    unfav_res = client.patch(f"/projects/{project_id}/favorite?favorite=false")
    assert unfav_res.status_code == 200
    assert unfav_res.json()["favorite"] is False

def test_archive_project():
    create_res = client.post("/projects", json={"name": "Archive Me"})
    project_id = create_res.json()["id"]
    
    arc_res = client.patch(f"/projects/{project_id}/archive")
    assert arc_res.status_code == 200
    assert arc_res.json()["status"] == ProjectStatus.ARCHIVED.value
    
    # Archiving again should be idempotent
    arc_res2 = client.patch(f"/projects/{project_id}/archive")
    assert arc_res2.status_code == 200
    assert arc_res2.json()["status"] == ProjectStatus.ARCHIVED.value
