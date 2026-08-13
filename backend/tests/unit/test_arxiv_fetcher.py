"""Test arXiv fetcher."""
import pytest
from unittest.mock import patch
from backend.app.core.fetcher.arxiv_fetcher import ArxivFetcher

xml_response = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2101.00001</id>
    <published>2021-01-01T00:00:00Z</published>
    <title>Test Title</title>
    <summary>Test Abstract</summary>
    <author>
      <name>Author One</name>
    </author>
    <link href="http://arxiv.org/pdf/2101.00001" title="pdf" type="application/pdf"/>
  </entry>
</feed>
"""

@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_arxiv_fetcher(mock_get):
    """Test basic fetcher functionality."""
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = xml_response
    mock_get.return_value.raise_for_status = lambda: None
    
    fetcher = ArxivFetcher()
    results = await fetcher.search("test", 1)
    
    assert len(results) == 1
    assert results[0].title == "Test Title"
    assert results[0].year == 2021
    assert results[0].pdf_url == "http://arxiv.org/pdf/2101.00001"
    assert results[0].source == "arxiv"
