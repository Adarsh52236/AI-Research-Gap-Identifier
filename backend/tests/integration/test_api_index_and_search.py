"""Integration test for index and search API."""
from fastapi.testclient import TestClient
from pathlib import Path
import json
from backend.app.main import app
from backend.app.config import settings
from backend.app.core.embeddings.embedding_generator import EmbeddingGenerator
from backend.app.api.v1.analysis import indexing_service, search_service
from backend.app.core.embeddings.vector_store import ChromaVectorStore
import pytest

client = TestClient(app)

def test_api_index_and_search(tmp_path, monkeypatch):
    storage_dir = tmp_path / "storage"
    processed_dir = storage_dir / "processed" / "paper_abc"
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    monkeypatch.setattr(settings, "STORAGE_DIR", str(storage_dir))
    monkeypatch.setattr(settings, "CHROMA_DB_PATH", str(storage_dir / "chroma"))
    monkeypatch.setattr(settings, "VECTOR_BACKEND", "chroma")
    
    isolated_store = ChromaVectorStore()
    indexing_service.store = isolated_store
    search_service.store = isolated_store
    
    def mock_embed(self, texts):
        return [[0.1] * 384 for _ in texts]
    monkeypatch.setattr(EmbeddingGenerator, "embed_texts", mock_embed)
    
    # write valid sections
    with open(processed_dir / "sections.json", "w", encoding="utf-8") as f:
        f.write(json.dumps({
            "ABSTRACT": "A"*300, # valid length
            "INTRODUCTION": "I"*300
        }))
        
    # Index
    resp1 = client.post("/api/v1/analysis/index-embeddings/", json={
        "paper_ids": ["paper_abc"],
        "sections": ["ABSTRACT", "INTRODUCTION"],
        "force_reindex": True
    })
    assert resp1.status_code == 200
    assert resp1.json()["indexed_count"] == 2
        
    # Search
    resp2 = client.post("/api/v1/analysis/similarity-search/", json={
        "query_text": "A",
        "top_k": 2
    })
    assert resp2.status_code == 200
    assert resp2.json()["count"] == 2
    assert resp2.json()["results"][0]["paper_id"] == "paper_abc"
