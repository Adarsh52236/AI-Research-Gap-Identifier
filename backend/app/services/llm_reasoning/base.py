from abc import ABC, abstractmethod

class LLMProvider(ABC):
    """Abstract interface for LLM providers."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the name of the LLM provider/model."""
        pass

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generates a text response based on the provided prompt."""
        pass
