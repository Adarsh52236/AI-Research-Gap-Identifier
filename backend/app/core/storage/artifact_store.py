from abc import ABC, abstractmethod
from typing import Optional
from pathlib import Path

class ArtifactStore(ABC):
    @abstractmethod
    def upload_file(self, local_path: str | Path, bucket: str, object_path: str) -> Optional[str]:
        """
        Uploads a file to the configured artifact store.
        Returns the remote path or URL if successful, else None.
        """
        pass
        
    @abstractmethod
    def download_file(self, bucket: str, object_path: str, local_dest: str | Path) -> bool:
        """
        Downloads a file from the artifact store to a local destination.
        Returns True if successful, False otherwise.
        """
        pass

def get_artifact_store() -> ArtifactStore:
    from backend.app.config import settings
    if settings.ARTIFACT_BACKEND.lower() == "supabase":
        from backend.app.core.storage.supabase_storage_store import SupabaseStorageStore
        return SupabaseStorageStore()
    else:
        from backend.app.core.storage.local_artifact_store import LocalArtifactStore
        return LocalArtifactStore()
