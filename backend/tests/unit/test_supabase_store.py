import pytest
from unittest.mock import patch, MagicMock, mock_open
from backend.app.core.storage.supabase_storage_store import SupabaseStorageStore
from backend.app.config import settings

@pytest.fixture
def mock_settings():
    original_url = settings.SUPABASE_URL
    original_key = settings.SUPABASE_SERVICE_ROLE_KEY
    settings.SUPABASE_URL = "https://mock.supabase.co"
    settings.SUPABASE_SERVICE_ROLE_KEY = "mock_key"
    yield
    settings.SUPABASE_URL = original_url
    settings.SUPABASE_SERVICE_ROLE_KEY = original_key

@patch('backend.app.core.storage.supabase_storage_store.create_client')
@patch('backend.app.core.storage.supabase_storage_store.Path.exists', return_value=True)
def test_supabase_upload(mock_exists, mock_create_client, mock_settings):
    mock_client = MagicMock()
    mock_create_client.return_value = mock_client
    
    # Mock file upload
    store = SupabaseStorageStore()
    
    with patch("builtins.open", mock_open(read_data="dummy")):
        res = store.upload_file("dummy.pdf", "documents", "path/to/dummy.pdf")
        
    assert res == "documents/path/to/dummy.pdf"
    assert mock_client.storage.from_.called
    assert mock_client.storage.from_().upload.called

@patch('backend.app.core.storage.supabase_storage_store.create_client')
def test_supabase_download(mock_create_client, mock_settings):
    mock_client = MagicMock()
    mock_create_client.return_value = mock_client
    mock_client.storage.from_().download.return_value = b"dummy content"
    
    store = SupabaseStorageStore()
    
    with patch('backend.app.core.storage.supabase_storage_store.Path.mkdir'):
        with patch("builtins.open", mock_open()) as mocked_file:
            res = store.download_file("documents", "path/to/dummy.pdf", "local/dummy.pdf")
            
    assert res is True
    mocked_file().write.assert_called_once_with(b"dummy content")
