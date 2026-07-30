import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid

from app.main import app
from app.database.base import Base
from app.database.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.analysis import Analysis
from app.core.security import hash_password

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_authorization.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()



client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()

def create_user_and_token(email: str, username: str):
    client.post("/api/v1/auth/register", json={
        "full_name": "Test User",
        "email": email,
        "username": username,
        "password": "password123"
    })
    resp = client.post("/api/v1/auth/login", data={"username": email, "password": "password123"})
    return resp.json()["access_token"]

def test_user_creates_project_auto_linked():
    token = create_user_and_token("user1@example.com", "user1")
    resp = client.post(
        "/projects",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "My Project", "description": "Test"}
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "My Project"
    
    # Verify via direct DB query that user_id is set
    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == "user1@example.com").first()
    proj = db.query(Project).filter(Project.id == uuid.UUID(data["id"])).first()
    assert proj.user_id == user.id
    db.close()

def test_user_accesses_own_project():
    token = create_user_and_token("user1@example.com", "user1")
    resp = client.post(
        "/projects",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "My Project"}
    )
    proj_id = resp.json()["id"]
    
    # Access it
    get_resp = client.get(
        f"/projects/{proj_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_resp.status_code == 200

def test_user_cannot_access_another_users_project():
    token1 = create_user_and_token("user1@example.com", "user1")
    resp = client.post(
        "/projects",
        headers={"Authorization": f"Bearer {token1}"},
        json={"name": "User 1 Project"}
    )
    proj_id = resp.json()["id"]
    
    # User 2 tries to access User 1's project
    token2 = create_user_and_token("user2@example.com", "user2")
    get_resp = client.get(
        f"/projects/{proj_id}",
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert get_resp.status_code == 404

def test_project_listing_only_returns_owned_projects():
    token1 = create_user_and_token("user1@example.com", "user1")
    token2 = create_user_and_token("user2@example.com", "user2")
    
    client.post("/projects", headers={"Authorization": f"Bearer {token1}"}, json={"name": "Proj 1"})
    client.post("/projects", headers={"Authorization": f"Bearer {token2}"}, json={"name": "Proj 2"})
    
    list1 = client.get("/projects", headers={"Authorization": f"Bearer {token1}"}).json()
    assert len(list1) == 1
    assert list1[0]["name"] == "Proj 1"
    
    list2 = client.get("/projects", headers={"Authorization": f"Bearer {token2}"}).json()
    assert len(list2) == 1
    assert list2[0]["name"] == "Proj 2"

def test_user_updates_own_project():
    token = create_user_and_token("user1@example.com", "user1")
    resp = client.post("/projects", headers={"Authorization": f"Bearer {token}"}, json={"name": "Project 1"})
    proj_id = resp.json()["id"]
    
    resp = client.put(f"/projects/{proj_id}", headers={"Authorization": f"Bearer {token}"}, json={"name": "P1 Updated"})
    assert resp.status_code == 200

def test_updating_another_users_project_returns_404():
    token1 = create_user_and_token("user1@example.com", "user1")
    resp = client.post("/projects", headers={"Authorization": f"Bearer {token1}"}, json={"name": "Project 1"})
    proj_id = resp.json()["id"]
    
    token2 = create_user_and_token("user2@example.com", "user2")
    resp = client.put(f"/projects/{proj_id}", headers={"Authorization": f"Bearer {token2}"}, json={"name": "P1 Hacked"})
    assert resp.status_code == 404

def test_deleting_another_users_project_returns_404():
    token1 = create_user_and_token("user1@example.com", "user1")
    resp = client.post("/projects", headers={"Authorization": f"Bearer {token1}"}, json={"name": "Project 1"})
    proj_id = resp.json()["id"]
    
    token2 = create_user_and_token("user2@example.com", "user2")
    resp = client.delete(f"/projects/{proj_id}", headers={"Authorization": f"Bearer {token2}"})
    assert resp.status_code == 404

def test_soft_deleted_owned_project_returns_404():
    token = create_user_and_token("user1@example.com", "user1")
    resp = client.post("/projects", headers={"Authorization": f"Bearer {token}"}, json={"name": "Project 1"})
    proj_id = resp.json()["id"]
    
    client.delete(f"/projects/{proj_id}", headers={"Authorization": f"Bearer {token}"})
    
    resp = client.get(f"/projects/{proj_id}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 404

def test_analysis_ownership():
    token1 = create_user_and_token("user1@example.com", "user1")
    token2 = create_user_and_token("user2@example.com", "user2")
    
    # 1 creates project
    resp = client.post("/projects", headers={"Authorization": f"Bearer {token1}"}, json={"name": "Project 1"})
    proj_id = resp.json()["id"]
    
    # 2 tries to create analysis in 1's project -> 404
    resp = client.post(f"/api/v1/projects/{proj_id}/analyses?query=test", headers={"Authorization": f"Bearer {token2}"})
    assert resp.status_code == 404
    
    # We can't fully run analysis in test easily if it depends on AI, 
    # but we will mock or bypass it if we want, or expect a 500 if the AI isn't mocked in this test.
    # The important part is that we get 404 for User 2.
    
    # Let's manually inject an analysis into the DB for User 1's project
    db = TestingSessionLocal()
    analysis = Analysis(project_id=uuid.UUID(proj_id), query="test")
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    analysis_id = analysis.id
    db.close()
    
    # 1 accesses -> 200
    resp = client.get(f"/api/v1/analyses/{analysis_id}", headers={"Authorization": f"Bearer {token1}"})
    assert resp.status_code == 200
    
    # 2 accesses -> 404
    resp = client.get(f"/api/v1/analyses/{analysis_id}", headers={"Authorization": f"Bearer {token2}"})
    assert resp.status_code == 404
    
    # 2 lists -> 404 (because project belongs to 1)
    resp = client.get(f"/api/v1/projects/{proj_id}/analyses", headers={"Authorization": f"Bearer {token2}"})
    assert resp.status_code == 404
    
    # 2 deletes -> 404
    resp = client.delete(f"/api/v1/analyses/{analysis_id}", headers={"Authorization": f"Bearer {token2}"})
    assert resp.status_code == 404
    
    # 1 deletes -> 204
    resp = client.delete(f"/api/v1/analyses/{analysis_id}", headers={"Authorization": f"Bearer {token1}"})
    assert resp.status_code == 204
    
    # 1 accesses after delete -> 404
    resp = client.get(f"/api/v1/analyses/{analysis_id}", headers={"Authorization": f"Bearer {token1}"})
    assert resp.status_code == 404


def test_duplicate_project_names_allowed_across_different_users():
    token1 = create_user_and_token("user3@example.com", "user3")
    token2 = create_user_and_token("user4@example.com", "user4")
    
    resp1 = client.post("/projects", headers={"Authorization": f"Bearer {token1}"}, json={"name": "Duplicate Name"})
    assert resp1.status_code == 201
    
    resp2 = client.post("/projects", headers={"Authorization": f"Bearer {token2}"}, json={"name": "Duplicate Name"})
    assert resp2.status_code == 201

def test_duplicate_project_names_rejected_for_same_user():
    token = create_user_and_token("user5@example.com", "user5")
    
    resp1 = client.post("/projects", headers={"Authorization": f"Bearer {token}"}, json={"name": "Unique Name"})
    assert resp1.status_code == 201
    
    resp2 = client.post("/projects", headers={"Authorization": f"Bearer {token}"}, json={"name": "Unique Name"})
    assert resp2.status_code == 409
    
    # Soft delete the first project
    proj_id = resp1.json()["id"]
    client.delete(f"/projects/{proj_id}", headers={"Authorization": f"Bearer {token}"})
    
    # Now creating the same name should work because the previous is soft-deleted
    resp3 = client.post("/projects", headers={"Authorization": f"Bearer {token}"}, json={"name": "Unique Name"})
    assert resp3.status_code == 201

def test_soft_deleted_parent_hides_child_analyses():
    token = create_user_and_token("user6@example.com", "user6")
    
    resp = client.post("/projects", headers={"Authorization": f"Bearer {token}"}, json={"name": "Project to Delete"})
    proj_id = resp.json()["id"]
    
    # Inject analysis
    db = TestingSessionLocal()
    analysis = Analysis(project_id=uuid.UUID(proj_id), query="test query")
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    analysis_id = analysis.id
    db.close()
    
    # Verify accessible
    get_resp = client.get(f"/api/v1/analyses/{analysis_id}", headers={"Authorization": f"Bearer {token}"})
    assert get_resp.status_code == 200
    
    # Soft delete project
    client.delete(f"/projects/{proj_id}", headers={"Authorization": f"Bearer {token}"})
    
    # Verify analysis is hidden
    get_resp2 = client.get(f"/api/v1/analyses/{analysis_id}", headers={"Authorization": f"Bearer {token}"})
    assert get_resp2.status_code == 404

def test_update_after_soft_delete_returns_404():
    token = create_user_and_token("user7@example.com", "user7")
    resp = client.post("/projects", headers={"Authorization": f"Bearer {token}"}, json={"name": "Project 7"})
    proj_id = resp.json()["id"]
    
    client.delete(f"/projects/{proj_id}", headers={"Authorization": f"Bearer {token}"})
    
    update_resp = client.put(f"/projects/{proj_id}", headers={"Authorization": f"Bearer {token}"}, json={"name": "Updated 7"})
    assert update_resp.status_code == 404
