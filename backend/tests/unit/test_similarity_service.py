"""Tests for similarity service."""
from backend.app.core.embeddings.similarity_search import SimilaritySearchService
from backend.app.core.embeddings.vector_store import ChromaVectorStore
from backend.app.core.embeddings.embedding_generator import EmbeddingGenerator
from backend.app.config import settings

def test_similarity_search(tmp_path, monkeypatch):
    # Mock Chroma path
    monkeypatch.setattr(settings, "CHROMA_DB_PATH", str(tmp_path / "chroma"))
    monkeypatch.setattr(settings, "VECTOR_BACKEND", "chroma")
    
    # Mock Embeddings
    def mock_embed(self, texts):
        return [[0.1] * 384 for _ in texts]
    monkeypatch.setattr(EmbeddingGenerator, "embed_texts", mock_embed)
    
    # Setup Store
    store = ChromaVectorStore()
    store.upsert_texts([{
        "id": "p1:ABSTRACT",
        "text": "mock text",
        "embedding": [0.1] * 384,
        "metadata": {"paper_id": "p1", "section": "ABSTRACT"}
    }])
    
    # Query
    svc = SimilaritySearchService()
    resp = svc.search("query", top_k=10, filter_source=None, filter_year_from=None, filter_year_to=None, filter_section=None)
    
    assert resp.count == 1
    assert resp.results[0].paper_id == "p1"
    assert resp.results[0].score == 1.0
