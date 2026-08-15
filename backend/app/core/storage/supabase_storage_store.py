import mimetypes
from pathlib import Path
from typing import Optional
from supabase import create_client, Client
from backend.app.config import settings
from backend.app.core.storage.artifact_store import ArtifactStore
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)

class SupabaseStorageStore(ArtifactStore):
    def __init__(self):
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set for Supabase artifact backend")
        
        # We use service role key to bypass RLS for server-side uploads
        self.client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
        
    def upload_file(self, local_path: str | Path, bucket: str, object_path: str) -> Optional[str]:
        """Uploads file to Supabase Storage."""
        p = Path(local_path)
        if not p.exists():
            logger.error(f"Cannot upload {local_path}: File does not exist")
            return None
            
        content_type, _ = mimetypes.guess_type(str(p))
        if not content_type:
            content_type = "application/octet-stream"
            
        try:
            with open(p, "rb") as f:
                res = self.client.storage.from_(bucket).upload(
                    path=object_path,
                    file=f,
                    file_options={"content-type": content_type, "upsert": "true"}
                )
                
            # If successful, return the public URL (assuming public bucket for simplicity)
            # Alternatively, we could just return bucket/object_path to store in DB
            # We will return the object path, then generate public URL when needed, or just return object_path
            return f"{bucket}/{object_path}"
        except Exception as e:
            logger.error(f"Supabase upload failed for {object_path}: {e}")
            return None

    def download_file(self, bucket: str, object_path: str, local_dest: str | Path) -> bool:
        """Downloads file from Supabase Storage."""
        try:
            res = self.client.storage.from_(bucket).download(object_path)
            
            dest = Path(local_dest)
            dest.parent.mkdir(parents=True, exist_ok=True)
            
            with open(dest, "wb") as f:
                f.write(res)
                
            return True
        except Exception as e:
            logger.error(f"Supabase download failed for {object_path}: {e}")
            return False
