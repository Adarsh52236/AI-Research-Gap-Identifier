"""Test Semantic Scholar fetcher."""
import pytest
from unittest.mock import patch
from backend.app.core.fetcher.semantic_scholar_fetcher import SemanticScholarFetcher

json_response = {
    "data": [
        {
            "paperId": "abcdef12345",
            "title": "Test Title SS",
            "year": 2022,
            "abstract": "Test Abstract SS",
            "authors": [{"name": "Author Two"}],
            "url": "https://semanticscholar.org/paper/abcdef12345",
            "openAccessPdf": {"url": "https://example.com/paper.pdf"}
        }
    ]
}

@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_semantic_scholar_fetcher(mock_get):
    """Test basic fetcher functionality."""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json = lambda: json_response
    mock_get.return_value.raise_for_status = lambda: None
    
    fetcher = SemanticScholarFetcher()
    results = await fetcher.search("test", 1)
    
    assert len(results) == 1
    assert results[0].title == "Test Title SS"
    assert results[0].year == 2022
    assert results[0].pdf_url == "https://example.com/paper.pdf"
    assert results[0].source == "semantic_scholar"
