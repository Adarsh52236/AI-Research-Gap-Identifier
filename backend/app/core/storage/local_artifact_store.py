import shutil
from pathlib import Path
from typing import Optional
from backend.app.core.storage.artifact_store import ArtifactStore

class LocalArtifactStore(ArtifactStore):
    def upload_file(self, local_path: str | Path, bucket: str, object_path: str) -> Optional[str]:
        """
        In the local backend, we do not need to upload anything because 
        the files are already saved to the local persistent disk.
        We'll just return the original local_path as the 'remote' path.
        """
        return str(local_path)
        
    def download_file(self, bucket: str, object_path: str, local_dest: str | Path) -> bool:
        """
        In local mode, the object_path is actually the local path.
        """
        try:
            if str(object_path) != str(local_dest):
                # Copy from the 'remote' local path to the destination if different
                Path(local_dest).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(object_path, local_dest)
            return True
        except Exception:
            return False
