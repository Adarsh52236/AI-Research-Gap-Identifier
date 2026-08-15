import sys
import asyncio
from sqlalchemy import text
from supabase import create_client

from backend.app.config import settings
from backend.app.db.session import SessionLocal
from backend.app.core.storage.artifact_store import get_artifact_store
from backend.app.core.embeddings.vector_store import get_vector_store

def check_database():
    print("Checking Database Connection...")
    if not settings.DATABASE_URL:
        print("[FAIL] DATABASE_URL is not set.")
        return False
        
    try:
        db = SessionLocal()
        # 1. Select 1
        db.execute(text("SELECT 1"))
        print("[OK] Database connection successful (SELECT 1).")
        
        # 2. Check pgvector extension
        res = db.execute(text("SELECT extname FROM pg_extension WHERE extname = 'vector'")).fetchone()
        if res:
            print("[OK] pgvector extension exists.")
        else:
            print("[FAIL] pgvector extension is NOT installed.")
            return False
            
        # 3. Check vectors table
        res = db.execute(text("SELECT to_regclass('paper_section_vectors')")).scalar()
        if res:
            print("[OK] 'paper_section_vectors' table exists.")
        else:
            print("[FAIL] 'paper_section_vectors' table does NOT exist.")
            return False
            
        db.close()
        return True
    except Exception as e:
        print(f"[FAIL] Database check failed: {e}")
        return False

def check_supabase_storage():
    print("Checking Supabase Storage...")
    if settings.ARTIFACT_BACKEND != "supabase":
        print("[INFO] Artifact backend is not supabase, skipping bucket check.")
        return True
        
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        print("[FAIL] Supabase URL or Key is missing.")
        return False
        
    try:
        client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
        buckets = client.storage.list_buckets()
        bucket_names = [b.name for b in buckets]
        
        if 'documents' in bucket_names:
            print("[OK] 'documents' storage bucket exists.")
            return True
        else:
            print("[FAIL] 'documents' storage bucket does NOT exist.")
            return False
    except Exception as e:
        print(f"[FAIL] Supabase Storage check failed: {e}")
        return False

async def dry_run_pipeline():
    print("Running Mock Pipeline Write Tests...")
    try:
        vector_store = get_vector_store()
        artifact_store = get_artifact_store()
        
        print(f"[OK] Vector Store Factory Initialized: {type(vector_store).__name__}")
        print(f"[OK] Artifact Store Factory Initialized: {type(artifact_store).__name__}")
        
        # 1. Test vector insertion
        try:
            vector_store.upsert_texts([{
                "id": "mock_test_123_chunk_1",
                "text": "This is a test vector",
                "embedding": [0.1] * 384,
                "metadata": {"test": True, "paper_id": "mock_test_123"}
            }])
            print("[OK] Vector Store upsert_texts executed successfully.")
        except Exception as ve:
            print(f"[FAIL] Vector Store upsert_texts failed: {ve}")
            return False

        # 2. Test Artifact Store
        import tempfile
        import os
        try:
            with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".txt") as tmp:
                tmp.write("mock artifact content")
                tmp_path = tmp.name
            
            res = artifact_store.upload_file(tmp_path, "documents", "mock_test_123/artifact.txt")
            print(f"[OK] Artifact Store upload_file executed successfully: {res}")
            os.remove(tmp_path)
        except Exception as ae:
            print(f"[FAIL] Artifact Store upload_file failed: {ae}")
            return False
            
        if settings.VECTOR_BACKEND == "pgvector" and settings.ARTIFACT_BACKEND == "supabase":
            print("[OK] All Free-Tier stateless backends are active.")
            return True
        else:
            print("[WARN] Running in local mode. Not fully stateless.")
            return True
            
    except Exception as e:
        print(f"[FAIL] Mock Pipeline Tests failed: {e}")
        return False

async def main():
    print(f"VECTOR_BACKEND: {settings.VECTOR_BACKEND}")
    print(f"ARTIFACT_BACKEND: {settings.ARTIFACT_BACKEND}")
    print("-" * 30)
    
    db_ok = check_database()
    storage_ok = check_supabase_storage()
    pipeline_ok = await dry_run_pipeline()
    
    print("-" * 30)
    if db_ok and storage_ok and pipeline_ok:
        print("[SUCCESS] DEPLOYMENT READINESS AUDIT PASSED")
        sys.exit(0)
    else:
        print("[ERROR] DEPLOYMENT READINESS AUDIT FAILED")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
