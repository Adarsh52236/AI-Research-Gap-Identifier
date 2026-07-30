import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid

from app.main import app
from app.database.base import Base
from app.database.database import get_db
from app.core.config import settings

# Test Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth.db"

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

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# =========================
# Registration Tests
# =========================

def test_register_user_success():
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "John Doe",
            "email": "johndoe@example.com",
            "username": "johndoe",
            "password": "securepassword123"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "johndoe@example.com"
    assert data["username"] == "johndoe"
    assert "password_hash" not in data
    assert "password" not in data

def test_register_duplicate_email():
    payload = {
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "username": "johndoe",
        "password": "securepassword123"
    }
    client.post("/api/v1/auth/register", json=payload)
    
    # Try with same email, different username
    payload["username"] = "different_username"
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_register_duplicate_username():
    payload = {
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "username": "johndoe",
        "password": "securepassword123"
    }
    client.post("/api/v1/auth/register", json=payload)
    
    # Try with different email, same username
    payload["email"] = "different@example.com"
    payload["username"] = "johndoe"
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400
    assert "Username already registered" in response.json()["detail"]

# =========================
# Login Tests
# =========================

def register_test_user():
    client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Jane Doe",
            "email": "jane@example.com",
            "username": "janedoe",
            "password": "my_password"
        }
    )

def test_login_success():
    register_test_user()
    
    # Login via form data (OAuth2PasswordRequestForm maps email to 'username' field)
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "jane@example.com",
            "password": "my_password"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_password():
    register_test_user()
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "jane@example.com",
            "password": "wrong_password"
        }
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"

def test_login_invalid_email():
    register_test_user()
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "wrong@example.com",
            "password": "my_password"
        }
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"

# =========================
# Protected Route (/me) Tests
# =========================

def test_get_me_success():
    register_test_user()
    login_resp = client.post(
        "/api/v1/auth/login",
        data={"username": "jane@example.com", "password": "my_password"}
    )
    token = login_resp.json()["access_token"]
    
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "jane@example.com"
    assert data["username"] == "janedoe"
    assert "password_hash" not in data

def test_get_me_no_token():
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_get_me_invalid_token():
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid_token_xyz"}
    )
    assert response.status_code == 401
    assert "Invalid authentication token" in response.json()["detail"]

# =========================
# JWT Expiration / Payload Tests
# =========================

def test_expired_token():
    # Hack the expire time to 0 by temporarily overriding settings
    register_test_user()
    
    original_expire = settings.access_token_expire_minutes
    settings.access_token_expire_minutes = -1 # Expires immediately
    
    try:
        login_resp = client.post(
            "/api/v1/auth/login",
            data={"username": "jane@example.com", "password": "my_password"}
        )
        token = login_resp.json()["access_token"]
        
        # Token is immediately expired
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 401
        assert "expired" in response.json()["detail"].lower()
    finally:
        settings.access_token_expire_minutes = original_expire

def test_invalid_token_type():
    import jwt
    from datetime import datetime, timezone, timedelta
    
    register_test_user()
    # Find user ID (to make it a valid sub)
    login_resp = client.post(
        "/api/v1/auth/login",
        data={"username": "jane@example.com", "password": "my_password"}
    )
    token = login_resp.json()["access_token"]
    user_data = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}).json()
    
    # Create fake token with wrong 'type'
    payload = {
        "sub": user_data["id"],
        "type": "refresh", # <--- wrong type
        "iat": datetime.now(timezone.utc).timestamp(),
        "exp": (datetime.now(timezone.utc) + timedelta(minutes=10)).timestamp(),
    }
    bad_token = jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)
    
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {bad_token}"})
    assert response.status_code == 401
    assert "Invalid token type" in response.json()["detail"]

def test_invalid_subject_format():
    import jwt
    from datetime import datetime, timezone, timedelta
    
    # Valid type, but 'sub' is not a UUID
    payload = {
        "sub": "not-a-uuid", 
        "type": "access",
        "iat": datetime.now(timezone.utc).timestamp(),
        "exp": (datetime.now(timezone.utc) + timedelta(minutes=10)).timestamp(),
    }
    bad_token = jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)
    
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {bad_token}"})
    assert response.status_code == 401
    assert "Invalid token subject format" in response.json()["detail"]
