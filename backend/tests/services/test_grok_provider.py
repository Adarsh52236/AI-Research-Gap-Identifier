import pytest
import httpx
from unittest.mock import patch, MagicMock
from app.services.llm_reasoning.grok_provider import GrokLLMProvider
from app.services.llm_reasoning.exceptions import (
    LLMConfigurationError,
    LLMRateLimitError,
    LLMProviderError,
    LLMTimeoutError,
    LLMNetworkError
)

def test_missing_api_key():
    with pytest.raises(LLMConfigurationError):
        GrokLLMProvider(api_key="")

def test_successful_generation():
    provider = GrokLLMProvider(api_key="fake-key")
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": "{\"summary\": \"success\"}"
                }
            }
        ],
        "usage": {"total_tokens": 42}
    }
    
    with patch("httpx.Client.post", return_value=mock_response):
        result = provider.generate("test prompt")
        assert result == "{\"summary\": \"success\"}"

def test_rate_limit_error():
    provider = GrokLLMProvider(api_key="fake-key")
    
    mock_response = MagicMock()
    mock_response.status_code = 429
    
    with patch("httpx.Client.post", return_value=mock_response):
        with pytest.raises(LLMRateLimitError):
            provider.generate("test prompt")

def test_auth_error():
    provider = GrokLLMProvider(api_key="fake-key")
    
    mock_response = MagicMock()
    mock_response.status_code = 401
    
    with patch("httpx.Client.post", return_value=mock_response):
        with pytest.raises(LLMProviderError) as exc:
            provider.generate("test prompt")
        assert "authentication failed" in str(exc.value).lower()

def test_timeout_error():
    provider = GrokLLMProvider(api_key="fake-key")
    
    # We must patch the client context manager to yield a client that raises
    with patch("httpx.Client.post", side_effect=httpx.TimeoutException("timeout")):
        with pytest.raises(LLMTimeoutError):
            provider.generate("test prompt")

def test_network_error():
    provider = GrokLLMProvider(api_key="fake-key")
    
    with patch("httpx.Client.post", side_effect=httpx.RequestError("network down")):
        with pytest.raises(LLMNetworkError):
            provider.generate("test prompt")
