import os
from typing import List, Dict, Any, Optional
from app.core.logging import logger

from .base import VectorStore
from .models import SearchResult
from .exceptions import VectorStoreError, CollectionError

try:
    import chromadb
except ImportError:
    chromadb = None

class ChromaVectorStore(VectorStore):
    """Vector store implementation using ChromaDB."""
    
    def __init__(self, collection_name: str, persist_directory: str = "./chroma_db"):
        if chromadb is None:
            raise VectorStoreError("chromadb library is not installed.")
            
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        
        logger.info(f"Initializing ChromaVectorStore. Collection: {collection_name}, Path: {persist_directory}")
        
        try:
            # Create the directory if it doesn't exist
            os.makedirs(persist_directory, exist_ok=True)
            self.client = chromadb.PersistentClient(path=persist_directory)
            self.collection = self.client.get_or_create_collection(name=collection_name)
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB collection: {e}")
            raise CollectionError(f"Failed to initialize collection {collection_name}: {e}") from e

    def add_embeddings(
        self, 
        ids: List[str], 
        embeddings: List[List[float]], 
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        logger.info(f"Adding {len(ids)} embeddings to ChromaDB collection {self.collection_name}.")
        try:
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas
            )
            logger.info("Embeddings added successfully.")
        except Exception as e:
            logger.error(f"Failed to add embeddings to ChromaDB: {e}")
            raise VectorStoreError(f"Failed to add embeddings: {e}") from e

    def search(
        self, 
        query_embedding: List[float], 
        limit: int = 10
    ) -> List[SearchResult]:
        logger.info(f"Searching ChromaDB collection {self.collection_name} with limit {limit}.")
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                include=["metadatas", "distances", "embeddings"]
            )
            
            search_results = []
            
            # ChromaDB returns a list of lists corresponding to the query embedding
            if not results["ids"] or not results["ids"][0]:
                logger.info("No matching results found in ChromaDB.")
                return []
                
            ids = results["ids"][0]
            distances = results["distances"][0] if "distances" in results and results["distances"] else [0.0] * len(ids)
            metadatas = results["metadatas"][0] if "metadatas" in results and results["metadatas"] else [{}] * len(ids)
            embeddings = results["embeddings"][0] if "embeddings" in results and results["embeddings"] else [None] * len(ids)
            
            for idx in range(len(ids)):
                search_results.append(SearchResult(
                    paper_id=ids[idx],
                    score=float(distances[idx]),
                    metadata=metadatas[idx] or {},
                    embedding=embeddings[idx]
                ))
                
            logger.info(f"Search completed. Found {len(search_results)} results.")
            return search_results
        except Exception as e:
            logger.error(f"Search failed in ChromaDB: {e}")
            raise VectorStoreError(f"Search failed: {e}") from e

    def delete(self, ids: List[str]) -> None:
        logger.info(f"Deleting {len(ids)} embeddings from ChromaDB collection {self.collection_name}.")
        try:
            self.collection.delete(ids=ids)
            logger.info("Embeddings deleted successfully.")
        except Exception as e:
            logger.error(f"Failed to delete embeddings from ChromaDB: {e}")
            raise VectorStoreError(f"Failed to delete embeddings: {e}") from e

    def count(self) -> int:
        try:
            total = self.collection.count()
            logger.info(f"ChromaDB collection {self.collection_name} contains {total} items.")
            return total
        except Exception as e:
            logger.error(f"Failed to count embeddings in ChromaDB: {e}")
            raise VectorStoreError(f"Failed to count embeddings: {e}") from e
