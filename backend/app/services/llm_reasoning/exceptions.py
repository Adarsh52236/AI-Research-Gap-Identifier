class LLMReasoningError(Exception):
    """Exception raised for general LLM reasoning failures."""
    pass

class PromptGenerationError(LLMReasoningError):
    """Exception raised when prompt generation fails."""
    pass

class LLMProviderError(LLMReasoningError):
    """Exception raised when the LLM provider fails."""
    pass

class LLMRateLimitError(LLMProviderError):
    """Exception raised when the LLM provider rate limit is exceeded."""
    pass

class LLMTimeoutError(LLMProviderError):
    """Exception raised when the LLM provider request times out."""
    pass

class LLMNetworkError(LLMProviderError):
    """Exception raised for network-related failures with the LLM provider."""
    pass

class LLMConfigurationError(LLMProviderError):
    """Exception raised for invalid LLM configuration (e.g., missing API key)."""
    pass
