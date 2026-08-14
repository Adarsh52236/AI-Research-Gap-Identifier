import sys
import os
import argparse
from pathlib import Path
import sqlalchemy

# Ensure backend can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.app.config import settings
from backend.app.db.session import engine, SessionLocal
from backend.app.db import models
from alembic.config import Config
from alembic import command

def main():
    print("=== Supabase/Alembic Integration Audit ===")
    if not settings.DB_ENABLED:
        print("FAIL: DB_ENABLED is False in settings.")
        sys.exit(1)
        
    db_url = settings.DATABASE_URL
    if db_url:
        # Redact password if present
        if "@" in db_url:
            creds, rest = db_url.split("@", 1)
            user = creds.split(":")[0] if ":" in creds else creds
            redacted_url = f"{user}:***@{rest}"
        else:
            redacted_url = db_url
        print(f"DATABASE_URL is set. Redacted: {redacted_url}")
    else:
        print("DATABASE_URL is NOT set. Fallback to SQLite expected.")
        
    if not engine:
        print("FAIL: Engine is None.")
        sys.exit(1)
        
    print(f"Dialect in use: {engine.dialect.name}")
    
    # 1. Test Connection
    print("\n--- 1. Testing Connection ---")
    try:
        with engine.connect() as conn:
            result = conn.execute(sqlalchemy.text("SELECT 1")).scalar()
            if result == 1:
                print("PASS: Successfully connected and ran 'SELECT 1'.")
            else:
                print(f"FAIL: Expected 1, got {result}")
                sys.exit(1)
    except Exception as e:
        print(f"FAIL: Database connection error:\n{e}")
        sys.exit(1)
        
    # 2. Alembic Verification
    print("\n--- 2. Alembic Migrations ---")
    alembic_cfg = Config(os.path.join(os.path.dirname(os.path.dirname(__file__)), "alembic.ini"))
    alembic_cfg.set_main_option("script_location", os.path.join(os.path.dirname(os.path.dirname(__file__)), "alembic"))
    
    try:
        command.upgrade(alembic_cfg, "head")
        print("PASS: Alembic 'upgrade head' completed without errors.")
    except Exception as e:
        print(f"FAIL: Alembic migration error:\n{e}")
        sys.exit(1)
        
    # 3. Check Critical Tables
    print("\n--- 3. Verifying Critical Tables ---")
    try:
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        expected = ["papers", "pipeline_runs", "reports", "gap_signals"]
        missing = [t for t in expected if t not in tables]
        if missing:
            print(f"FAIL: Missing expected tables: {missing}")
            sys.exit(1)
        else:
            print(f"PASS: All critical tables exist: {expected}")
    except Exception as e:
        print(f"FAIL: Table verification error:\n{e}")
        sys.exit(1)
        
    # 4. Insert Test Record
    print("\n--- 4. Test Write Permissions ---")
    try:
        db = SessionLocal()
        # Insert directly and then delete it
        try:
            p = models.Paper(paper_id="test_db_audit_123", title="Temp", source="test")
            # Clear it if it somehow exists from a previous failed run
            existing = db.query(models.Paper).filter_by(paper_id="test_db_audit_123").first()
            if existing:
                db.delete(existing)
                db.commit()
                
            db.add(p)
            db.commit()
            print("PASS: Successfully inserted test record.")
            
            db.delete(p)
            db.commit()
            print("PASS: Successfully deleted test record.")
        except Exception as e:
            db.rollback()
            print(f"FAIL: Write test failed:\n{e}")
            sys.exit(1)
        finally:
            db.close()
            
    except Exception as e:
        print(f"FAIL: Test write error:\n{e}")
        sys.exit(1)

    print("\nOVERALL: PASS")

if __name__ == "__main__":
    main()
