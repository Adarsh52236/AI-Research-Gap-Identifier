"""Chroma Vector Store."""
import chromadb
from pathlib import Path
from backend.app.config import settings

class ChromaVectorStore:
    def __init__(self):
        db_path = Path(settings.CHROMA_DB_PATH).resolve()
        self.client = chromadb.PersistentClient(path=str(db_path))
        self.collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
        
    def _clean_metadata(self, metadata: dict) -> dict:
        """Chroma doesn't accept None values in metadata."""
        return {k: v for k, v in metadata.items() if v is not None}

    def upsert_texts(self, items: list[dict]):
        """Upsert items into Chroma.
        items: list of dict with id, text, embedding, metadata
        """
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
        """Queries the vector store."""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where,
            include=["documents", "metadatas", "distances"]
        )
        return results
        
    def exists(self, ids: list[str]) -> list[bool]:
        """Check if IDs exist. (Chroma API workaround since no direct 'exists' method)"""
        if not ids:
            return []
            
        try:
            results = self.collection.get(ids=ids, include=[])
            existing_ids = set(results.get("ids", []))
            return [i in existing_ids for i in ids]
        except Exception:
            return [False] * len(ids)
