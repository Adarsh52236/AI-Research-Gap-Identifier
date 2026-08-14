import pytest
import sqlalchemy
from backend.app.config import settings

def test_supabase_connection_smoke():
    """
    Smoke test to verify we can connect to the database.
    Skips if DATABASE_URL is not set (e.g., in CI without real credentials).
    """
    db_url = settings.DATABASE_URL
    if not db_url:
        pytest.skip("DATABASE_URL is not set. Skipping smoke test.")
        
    from backend.app.db.session import engine
    assert engine is not None, "Engine should be initialized when DB is enabled."
    
    with engine.connect() as conn:
        result = conn.execute(sqlalchemy.text("SELECT 1")).scalar()
        assert result == 1, "Expected SELECT 1 to return 1"
