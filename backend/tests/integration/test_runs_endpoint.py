import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

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
