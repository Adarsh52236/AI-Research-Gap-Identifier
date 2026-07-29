from typing import List, Dict, Any, Optional
from app.core.logging import logger
from .base import VectorStore
from .models import SearchResult
from .exceptions import VectorStoreError

class VectorStoreService:
    """Service for handling orchestration of vector store operations using DI."""
    
    def __init__(self, store: VectorStore):
        """Accepts a VectorStore implementation through dependency injection."""
        self.store = store
        logger.info("VectorStoreService initialized.")
        
    def add_embeddings(
        self, 
        ids: List[str], 
        embeddings: List[List[float]], 
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """Stores a batch of embeddings in the underlying vector store."""
        logger.info(f"VectorStoreService: adding {len(ids)} embeddings.")
        self.store.add_embeddings(ids, embeddings, metadatas)
        
    def search(
        self, 
        query_embedding: List[float], 
        limit: int = 10
    ) -> List[SearchResult]:
        """Searches the underlying vector store for the closest embeddings."""
        logger.info(f"VectorStoreService: searching for top {limit} closest embeddings.")
        return self.store.search(query_embedding, limit)
        
    def delete(self, ids: List[str]) -> None:
        """Deletes vectors from the store by their IDs."""
        logger.info(f"VectorStoreService: deleting {len(ids)} embeddings.")
        self.store.delete(ids)
        
    def count(self) -> int:
        """Returns the total number of vectors in the store."""
        return self.store.count()
