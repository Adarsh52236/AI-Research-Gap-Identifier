import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.deps import get_current_user
from backend.app.db.models import User

def mock_get_current_user():
    return User(id=1, username="test", email="test@test.com")

app.dependency_overrides[get_current_user] = mock_get_current_user

client = TestClient(app)

def test_list_runs():
    """Test the GET /api/v1/analysis/runs endpoint."""
    response = client.get("/api/v1/analysis/runs")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # If there are runs, check schema
    if len(data) > 0:
        run = data[0]
        assert "run_id" in run
        assert "status" in run
