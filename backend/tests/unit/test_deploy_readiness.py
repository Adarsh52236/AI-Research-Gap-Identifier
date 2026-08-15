import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Using an explicit import path to run functions for tests
from backend.scripts.deploy_readiness_check import check_database, check_supabase_storage, dry_run_pipeline

@patch("backend.scripts.deploy_readiness_check.settings.DATABASE_URL", "postgresql://fake")
@patch("backend.scripts.deploy_readiness_check.SessionLocal")
def test_check_database_success(mock_session):
    mock_db = MagicMock()
    # Mocking select 1, pg_extension, and vectors table existence
    mock_db.execute.return_value.fetchone.return_value = ("vector",)
    mock_db.execute.return_value.scalar.return_value = "paper_section_vectors"
    mock_session.return_value = mock_db

    assert check_database() is True

@patch("backend.scripts.deploy_readiness_check.create_client")
def test_check_supabase_storage_success(mock_create_client):
    mock_client = MagicMock()
    mock_bucket = MagicMock()
    mock_bucket.name = "documents"
    mock_client.storage.list_buckets.return_value = [mock_bucket]
    mock_create_client.return_value = mock_client
    
    assert check_supabase_storage() is True

@pytest.mark.asyncio
@patch("backend.scripts.deploy_readiness_check.get_artifact_store")
@patch("backend.scripts.deploy_readiness_check.get_vector_store")
async def test_dry_run_pipeline_success(mock_get_vector, mock_get_artifact):
    mock_vector = MagicMock()
    mock_get_vector.return_value = mock_vector
    
    mock_artifact = MagicMock()
    mock_artifact.upload_file.return_value = "documents/mock_test_123/artifact.txt"
    mock_get_artifact.return_value = mock_artifact
    
    assert await dry_run_pipeline() is True
    # Ensure our mocks were actually called by the readiness script
    mock_vector.upsert_texts.assert_called_once()
    mock_artifact.upload_file.assert_called_once()
