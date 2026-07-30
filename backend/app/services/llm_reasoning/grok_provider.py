import httpx
import time
from app.core.logging import logger
from .base import LLMProvider
from .exceptions import (
    LLMProviderError,
    LLMTimeoutError,
    LLMRateLimitError,
    LLMNetworkError,
    LLMConfigurationError
)

class GrokLLMProvider(LLMProvider):
    """Grok LLM integration via xAI chat completions API."""
    
    API_URL = "https://api.x.ai/v1/chat/completions"
    
    def __init__(self, api_key: str, model_name: str = "grok-beta", timeout: int = 60):
        if not api_key:
            raise LLMConfigurationError("GROK_API_KEY is missing or empty.")
            
        self._api_key = api_key
        self.model_name = model_name
        self.timeout = timeout
        
    @property
    def name(self) -> str:
        return self.model_name
        
    def generate(self, prompt: str) -> str:
        """
        Calls the Grok API synchronously to generate a response.
        Handles errors gracefully and returns the text response.
        """
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert AI research assistant. Provide your reasoning strictly in JSON format as requested."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "model": self.model_name,
            "stream": False,
            "temperature": 0.1,  # Low temperature for analytical reasoning
        }
        
        logger.info(f"[GrokLLMProvider] Sending request to {self.API_URL} using model {self.model_name}")
        start_time = time.perf_counter()
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(self.API_URL, headers=headers, json=payload)
                
                # Check for rate limiting
                if response.status_code == 429:
                    raise LLMRateLimitError("Grok API rate limit exceeded (429).")
                
                # Check for auth errors
                if response.status_code == 401:
                    raise LLMProviderError("Grok API authentication failed (401). Invalid API key.")
                    
                # Ensure other HTTP errors raise an exception
                response.raise_for_status()
                
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                
                # Log token usage if available
                usage = data.get("usage", {})
                total_tokens = usage.get("total_tokens", "unknown")
                latency = time.perf_counter() - start_time
                
                logger.info(f"[GrokLLMProvider] Request completed in {latency:.2f}s. Total tokens: {total_tokens}")
                
                return content
                
        except (LLMProviderError, LLMRateLimitError, LLMTimeoutError, LLMNetworkError):
            # Let custom exceptions bubble up
            raise
        except httpx.TimeoutException as e:
            logger.error(f"[GrokLLMProvider] Request timed out after {self.timeout}s.")
            raise LLMTimeoutError(f"Request to Grok API timed out: {e}") from e
        except httpx.RequestError as e:
            logger.error(f"[GrokLLMProvider] Network error: {e}")
            raise LLMNetworkError(f"Network error communicating with Grok API: {e}") from e
        except httpx.HTTPStatusError as e:
            logger.error(f"[GrokLLMProvider] API returned HTTP error: {e.response.status_code} - {e.response.text}")
            raise LLMProviderError(f"Grok API HTTP Error {e.response.status_code}: {e.response.text}") from e
        except (KeyError, IndexError) as e:
            logger.error(f"[GrokLLMProvider] Malformed API response structure.")
            raise LLMProviderError("Received malformed response structure from Grok API.") from e
        except Exception as e:
            logger.exception(f"[GrokLLMProvider] Unexpected error during generate.")
            raise LLMProviderError(f"Unexpected error during Grok API generation: {e}") from e
