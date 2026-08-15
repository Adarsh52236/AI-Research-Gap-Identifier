import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.session import SessionLocal
from backend.app.db.models import User
from backend.app.core.auth_utils import get_password_hash
import uuid

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    db = SessionLocal()
    unique_suffix = str(uuid.uuid4())[:8]
    testuser = f"testuser_{unique_suffix}"
    newuser = f"newuser_{unique_suffix}"
    
    user = User(username=testuser, email=f"test_{unique_suffix}@example.com", hashed_password=get_password_hash("password123"))
    db.add(user)
    db.commit()
    db.close()
    yield testuser, newuser
    db = SessionLocal()
    db.query(User).filter(User.username.in_([testuser, newuser])).delete()
    db.commit()
    db.close()

def test_signup_password_too_long(setup_db):
    testuser, newuser = setup_db
    long_password = "a" * 80
    response = client.post("/api/v1/auth/signup", json={
        "username": newuser,
        "email": f"{newuser}@example.com",
        "password": long_password
    })
    assert response.status_code == 400
    assert "too long" in response.json()["detail"].lower()

def test_login_form_password_too_long(setup_db):
    testuser, newuser = setup_db
    long_password = "a" * 80
    response = client.post("/api/v1/auth/login", data={
        "username": testuser,
        "password": long_password
    })
    assert response.status_code == 400
    assert "too long" in response.json()["detail"].lower()

def test_login_json_password_too_long(setup_db):
    testuser, newuser = setup_db
    long_password = "a" * 80
    response = client.post("/api/v1/auth/login-json", json={
        "username": testuser,
        "password": long_password
    })
    assert response.status_code == 400
    assert "too long" in response.json()["detail"].lower()

def test_login_wrong_creds_401(setup_db):
    testuser, newuser = setup_db
    response = client.post("/api/v1/auth/login-json", json={
        "username": testuser,
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    
    response = client.post("/api/v1/auth/login", data={
        "username": testuser,
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_login_json_missing_fields(setup_db):
    testuser, newuser = setup_db
    response = client.post("/api/v1/auth/login-json", json={
        "username": testuser
        # missing password
    })
    assert response.status_code == 422 # Pydantic validation error
