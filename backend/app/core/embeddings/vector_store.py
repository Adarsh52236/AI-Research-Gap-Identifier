"""Vector Store abstractions."""
import chromadb
from pathlib import Path
from abc import ABC, abstractmethod
from backend.app.config import settings

class VectorStore(ABC):
    @abstractmethod
    def upsert_texts(self, items: list[dict]):
        """
        Upsert items into the vector store.
        items: list of dict with id, text, embedding, metadata
        """
        pass
        
    @abstractmethod
    def query(self, query_embedding: list[float], top_k: int, where: dict | None = None) -> dict:
        """
        Queries the vector store.
        Returns a dictionary shaped like Chroma's response for backward compatibility:
        {
            "ids": [[id1, id2, ...]],
            "distances": [[dist1, dist2, ...]],
            "documents": [[doc1, doc2, ...]],
            "metadatas": [[meta1, meta2, ...]]
        }
        """
        pass
        
    @abstractmethod
    def exists(self, ids: list[str]) -> list[bool]:
        """Check if IDs exist."""
        pass


class ChromaVectorStore(VectorStore):
    def __init__(self):
        db_path = Path(settings.CHROMA_DB_PATH).resolve()
        self.client = chromadb.PersistentClient(path=str(db_path))
        self.collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
        
    def _clean_metadata(self, metadata: dict) -> dict:
        return {k: v for k, v in metadata.items() if v is not None}

    def upsert_texts(self, items: list[dict]):
        if not items:
            return
            
        ids = [item["id"] for item in items]
        embeddings = [item["embedding"] for item in items]
        documents = [item["text"] if item.get("text") else "" for item in items]
        metadatas = [self._clean_metadata(item["metadata"]) for item in items]
        
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        
    def query(self, query_embedding: list[float], top_k: int, where: dict | None = None) -> dict:
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where,
            include=["documents", "metadatas", "distances"]
        )
        
    def exists(self, ids: list[str]) -> list[bool]:
        if not ids:
            return []
            
        try:
            results = self.collection.get(ids=ids, include=[])
            existing_ids = set(results.get("ids", []))
            return [i in existing_ids for i in ids]
        except Exception:
            return [False] * len(ids)


def get_vector_store() -> VectorStore:
    if settings.VECTOR_BACKEND.lower() == "pgvector":
        from backend.app.core.embeddings.pgvector_store import PgVectorStore
        return PgVectorStore()
    else:
        return ChromaVectorStore()
