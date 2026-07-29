from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from .models import SearchResult

class VectorStore(ABC):
    """Abstract interface for all vector store providers."""
    
    @abstractmethod
    def add_embeddings(
        self, 
        ids: List[str], 
        embeddings: List[List[float]], 
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """Adds a batch of embeddings to the store."""
        pass
        
    @abstractmethod
    def search(
        self, 
        query_embedding: List[float], 
        limit: int = 10
    ) -> List[SearchResult]:
        """Searches the store for the closest embeddings."""
        pass
        
    @abstractmethod
    def delete(self, ids: List[str]) -> None:
        """Deletes vectors from the store by their IDs."""
        pass
        
    @abstractmethod
    def count(self) -> int:
        """Returns the total number of vectors in the store."""
        pass
