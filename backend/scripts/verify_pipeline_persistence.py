import sys
import os
import time
import json

# Ensure backend can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.app.config import settings
from backend.app.db.session import engine, SessionLocal
from backend.app.db import crud
from backend.app.db import models
from backend.app.db.schemas import PaperMetadata, PipelineRunStatus

def main():
    print("=== Pipeline Persistence Verification ===")
    
    if not settings.DB_ENABLED or not engine:
        print("FAIL: Database is disabled or engine is missing.")
        sys.exit(1)

    db = SessionLocal()
    try:
        # Mock Data
        test_paper_id = f"test_paper_{int(time.time())}"
        test_run_id = f"test_run_{int(time.time())}"
        
        print("\n--- 1. Writing Paper ---")
        paper_meta = PaperMetadata(
            paper_id=test_paper_id,
            title="Mock Persistence Paper",
            abstract="Testing persistence of the pipeline",
            authors=[],
            year=2024,
            source="test"
        )
        try:
            crud.upsert_paper(db, paper_meta)
            print("PASS: Mock paper written.")
        except Exception as e:
            print(f"FAIL: Could not write paper: {e}")
            db.rollback()
            sys.exit(1)

        print("\n--- 2. Writing PipelineRun ---")
        status = PipelineRunStatus(
            run_id=test_run_id,
            status="completed",
            started_at="2026-08-14T10:00:00Z",
            current_step=None,
            query="test query",
            steps=["search", "download", "extract", "mine", "index", "report"],
            papers_found=1
        )
        try:
            crud.create_or_update_run(db, status)
            print("PASS: Mock pipeline run written.")
        except Exception as e:
            print(f"FAIL: Could not write pipeline run: {e}")
            db.rollback()
            sys.exit(1)

        print("\n--- 3. Writing Report ---")
        try:
            row = models.ReportRow(
                run_id=test_run_id,
                query="test query",
                model="test-model",
                paper_ids_json=json.dumps([test_paper_id]),
                report_json_path="/tmp/test.json",
                report_md_path="/tmp/test.md"
            )
            db.add(row)
            db.commit()
            print("PASS: Mock report written.")
        except Exception as e:
            print(f"FAIL: Could not write report: {e}")
            db.rollback()
            sys.exit(1)
            
        print("\n--- 4. Querying Data Back ---")
        paper_count = db.query(models.Paper).filter_by(paper_id=test_paper_id).count()
        run_count = db.query(models.PipelineRunRow).filter_by(run_id=test_run_id).count()
        report_count = db.query(models.ReportRow).filter_by(run_id=test_run_id).count()
        
        print(f"Papers found: {paper_count} (Expected 1)")
        print(f"Runs found: {run_count} (Expected 1)")
        print(f"Reports found: {report_count} (Expected 1)")
        
        if paper_count == 1 and run_count == 1 and report_count == 1:
            print("PASS: Data successfully queried back.")
        else:
            print("FAIL: Counts do not match expected values.")
            sys.exit(1)
            
        print("\n--- 5. Cleanup ---")
        try:
            db.query(models.ReportRow).filter_by(run_id=test_run_id).delete()
            db.query(models.PipelineRunRow).filter_by(run_id=test_run_id).delete()
            db.query(models.Paper).filter_by(paper_id=test_paper_id).delete()
            db.commit()
            print("PASS: Mock data cleaned up.")
        except Exception as e:
            print(f"WARNING: Cleanup failed: {e}")
            
        print("\nOVERALL: PASS")

    finally:
        db.close()

if __name__ == "__main__":
    main()
