"""Test API search."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from backend.app.main import app
from backend.app.db.schemas import PaperMetadata

client = TestClient(app)

@patch("backend.app.api.v1.search.fetcher_manager.search_all")
def test_api_search(mock_search_all):
    """Test search API."""
    mock_search_all.return_value = [
        PaperMetadata(paper_id="1", title="Test Paper 1", source="arxiv"),
        PaperMetadata(paper_id="2", title="Test Paper 2", source="semantic_scholar")
    ]
    
    response = client.post("/api/v1/search/", json={"query": "graph neural networks", "limit": 5})
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2
    assert len(data["results"]) == 2
    assert data["results"][0]["title"] == "Test Paper 1"
