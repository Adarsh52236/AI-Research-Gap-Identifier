class LLMReasoningError(Exception):
    """Exception raised for general LLM reasoning failures."""
    pass

class PromptGenerationError(LLMReasoningError):
    """Exception raised when prompt generation fails."""
    pass

class LLMProviderError(LLMReasoningError):
    """Exception raised when the LLM provider fails."""
    pass
