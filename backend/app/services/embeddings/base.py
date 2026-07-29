from abc import ABC, abstractmethod
from typing import List
from .models import EmbeddingResult

class EmbeddingProvider(ABC):
    """Abstract interface for all embedding providers."""
    
    @abstractmethod
    def embed(self, text: str) -> EmbeddingResult:
        """Embeds a single string into a vector representation."""
        pass
        
    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[EmbeddingResult]:
        """Embeds a batch of strings into vector representations."""
        pass
