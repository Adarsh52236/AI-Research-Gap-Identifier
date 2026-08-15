import pytest
import json
from unittest.mock import patch, MagicMock
from backend.app.core.embeddings.pgvector_store import PgVectorStore

@patch('backend.app.core.embeddings.pgvector_store.SessionLocal')
def test_pgvector_store_upsert(mock_session_local):
    mock_db = MagicMock()
    mock_session_local.return_value = mock_db
    
    # Mock finding nothing (so it inserts)
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    store = PgVectorStore()
    
    items = [
        {"id": "doc1", "text": "Hello world", "embedding": [0.1]*384, "metadata": {"paper_id": "p1"}},
    ]
    
    store.upsert_texts(items)
    
    assert mock_db.add.called
    assert mock_db.commit.called
    assert mock_db.close.called

@patch('backend.app.core.embeddings.pgvector_store.SessionLocal')
def test_pgvector_store_query(mock_session_local):
    mock_db = MagicMock()
    mock_session_local.return_value = mock_db
    
    mock_row = MagicMock()
    mock_row.id = "doc1"
    mock_row.text = "Hello world"
    mock_row.metadata_json = json.dumps({"paper_id": "p1"})
    
    mock_db.execute.return_value.all.return_value = [(mock_row, 0.123)]
    
    store = PgVectorStore()
    res = store.query(query_embedding=[0.1]*384, top_k=1, where={"paper_id": "p1"})
    
    assert res["ids"] == [["doc1"]]
    assert res["distances"] == [[0.123]]
    assert res["documents"] == [["Hello world"]]
    assert res["metadatas"] == [[{"paper_id": "p1"}]]
    assert mock_db.close.called
