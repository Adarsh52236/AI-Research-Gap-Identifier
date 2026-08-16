import json
from pathlib import Path
from backend.app.config import settings
from backend.app.db.schemas import PipelineRunStatus
from backend.app.db.session import SessionLocal
from backend.app.db import crud
import os
import time
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)

class RunStore:
    """Abstract base class for pipeline run storage."""
    def create_run(self, status_obj: PipelineRunStatus) -> None:
        pass
        
    def update_run(self, run_id: str, status_obj: PipelineRunStatus) -> None:
        pass
        
    def append_event(self, run_id: str, event_dict: dict) -> None:
        pass
        
    def get_run(self, run_id: str) -> PipelineRunStatus | None:
        pass
        
    def list_runs(self, limit: int = 50, user_id: int | None = None) -> list[PipelineRunStatus]:
        pass
        
    def delete_run(self, run_id: str) -> bool:
        pass
        
    def delete_all_runs(self, user_id: int | None = None) -> int:
        pass
class LocalRunStore(RunStore):
    def __init__(self):
        self.runs_dir = Path(settings.RUNS_DIR)
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_run_dir(self, run_id: str) -> Path:
        run_dir = self.runs_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_dir

    def create_run(self, status_obj: PipelineRunStatus) -> None:
        self.update_run(status_obj.run_id, status_obj)
        
    def update_run(self, run_id: str, status_obj: PipelineRunStatus) -> None:
        run_dir = self._get_run_dir(run_id)
        status_path = run_dir / "status.json"
        
        temp_path = run_dir / "status.json.tmp"
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(status_obj.model_dump_json(indent=2))
            
        try:
            temp_path.replace(status_path)
        except PermissionError:
            time.sleep(0.1)
            try:
                temp_path.replace(status_path)
            except PermissionError:
                with open(status_path, "w", encoding="utf-8") as f:
                    f.write(status_obj.model_dump_json(indent=2))
                try:
                    temp_path.unlink()
                except OSError:
                    pass
        
    def get_run(self, run_id: str) -> PipelineRunStatus | None:
        status_path = self._get_run_dir(run_id) / "status.json"
        if not status_path.exists():
            return None
        with open(status_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return PipelineRunStatus(**data)
            
    def append_event(self, run_id: str, event_dict: dict) -> None:
        run_dir = self._get_run_dir(run_id)
        events_path = run_dir / "events.jsonl"
        with open(events_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event_dict) + "\n")
            
    def list_runs(self, limit: int = 50, user_id: int | None = None) -> list[PipelineRunStatus]:
        runs = []
        if self.runs_dir.exists():
            for run_id_dir in self.runs_dir.iterdir():
                if run_id_dir.is_dir():
                    status_file = run_id_dir / "status.json"
                    if status_file.exists():
                        try:
                            with open(status_file, "r", encoding="utf-8") as f:
                                data = json.load(f)
                                run_status = PipelineRunStatus(**data)
                                if user_id is None or run_status.user_id == user_id:
                                    runs.append(run_status)
                        except Exception as e:
                            logger.error(f"Error parsing run {run_id_dir.name}: {e}")
        runs.sort(key=lambda x: x.started_at or "", reverse=True)
        return runs[:limit]

    def delete_run(self, run_id: str) -> bool:
        run_dir = self._get_run_dir(run_id)
        if not run_dir.exists():
            return False
        import shutil
        shutil.rmtree(run_dir, ignore_errors=True)
        return True

    def delete_all_runs(self, user_id: int | None = None) -> int:
        deleted = 0
        if self.runs_dir.exists():
            for run_id_dir in self.runs_dir.iterdir():
                if run_id_dir.is_dir():
                    status_file = run_id_dir / "status.json"
                    if status_file.exists():
                        try:
                            with open(status_file, "r", encoding="utf-8") as f:
                                data = json.load(f)
                                run_status = PipelineRunStatus(**data)
                                if user_id is None or run_status.user_id == user_id:
                                    import shutil
                                    shutil.rmtree(run_id_dir, ignore_errors=True)
                                    deleted += 1
                        except Exception as e:
                            logger.error(f"Error parsing run {run_id_dir.name}: {e}")
        return deleted
class DBRunStore(RunStore):
    def _get_db(self):
        return SessionLocal()
        
    def create_run(self, status_obj: PipelineRunStatus) -> None:
        db = self._get_db()
        try:
            crud.create_or_update_run(db, status_obj)
        except Exception as e:
            logger.error(f"DBRunStore create_run failed for {status_obj.run_id}: {e}")
        finally:
            db.close()
            
    def update_run(self, run_id: str, status_obj: PipelineRunStatus) -> None:
        db = self._get_db()
        try:
            crud.create_or_update_run(db, status_obj)
        except Exception as e:
            logger.error(f"DBRunStore update_run failed for {run_id}: {e}")
        finally:
            db.close()
            
    def append_event(self, run_id: str, event_dict: dict) -> None:
        db = self._get_db()
        try:
            from backend.app.db.models import PipelineRunRow
            from sqlalchemy import select, update
            row = db.execute(select(PipelineRunRow).filter(PipelineRunRow.run_id == run_id)).scalar_one_or_none()
            if row:
                events = []
                if row.events_json:
                    try:
                        events = json.loads(row.events_json)
                    except:
                        pass
                events.append(event_dict)
                row.events_json = json.dumps(events)
                db.commit()
        except Exception as e:
            logger.error(f"DBRunStore append_event failed for {run_id}: {e}")
        finally:
            db.close()
            
    def get_run(self, run_id: str) -> PipelineRunStatus | None:
        db = self._get_db()
        try:
            from backend.app.db.models import PipelineRunRow
            from sqlalchemy import select
            row = db.execute(select(PipelineRunRow).filter(PipelineRunRow.run_id == run_id)).scalar_one_or_none()
            if row:
                status = PipelineRunStatus(
                    run_id=row.run_id,
                    session_id=row.session_id,
                    user_id=row.user_id,
                    status=row.status,
                    current_step=row.current_step,
                    query=row.query,
                    steps=json.loads(row.steps_json) if row.steps_json else [],
                    papers_found=row.papers_found,
                    papers_downloaded=row.papers_downloaded,
                    papers_extracted=row.papers_extracted,
                    papers_mined=row.papers_mined,
                    papers_indexed=row.papers_indexed,
                    report_path=row.report_path,
                    started_at=row.started_at.isoformat() + "Z" if row.started_at else ""
                )
                if row.finished_at:
                    status.finished_at = row.finished_at.isoformat() + "Z"
                if row.errors_json:
                    try:
                        status.errors = json.loads(row.errors_json)
                    except:
                        pass
                return status
            return None
        except Exception as e:
            logger.error(f"DBRunStore get_run failed for {run_id}: {e}")
            raise  # Do not return None on connection error to prevent 404s
        finally:
            db.close()
            
    def list_runs(self, limit: int = 50, user_id: int | None = None) -> list[PipelineRunStatus]:
        db = self._get_db()
        try:
            from backend.app.db.models import PipelineRunRow
            from sqlalchemy import select
            query = select(PipelineRunRow)
            if user_id is not None:
                query = query.filter(PipelineRunRow.user_id == user_id)
            query = query.order_by(PipelineRunRow.started_at.desc()).limit(limit)
            rows = db.execute(query).scalars().all()
            
            runs = []
            for row in rows:
                status = PipelineRunStatus(
                    run_id=row.run_id,
                    session_id=row.session_id,
                    user_id=row.user_id,
                    status=row.status,
                    current_step=row.current_step,
                    query=row.query,
                    steps=json.loads(row.steps_json) if row.steps_json else [],
                    papers_found=row.papers_found,
                    papers_downloaded=row.papers_downloaded,
                    papers_extracted=row.papers_extracted,
                    papers_mined=row.papers_mined,
                    papers_indexed=row.papers_indexed,
                    report_path=row.report_path,
                    started_at=row.started_at.isoformat() + "Z" if row.started_at else ""
                )
                if row.finished_at:
                    status.finished_at = row.finished_at.isoformat() + "Z"
                runs.append(status)
            return runs
        except Exception as e:
            logger.error(f"DBRunStore list_runs failed: {e}")
            return []
        finally:
            db.close()

    def delete_run(self, run_id: str) -> bool:
        db = self._get_db()
        try:
            from backend.app.db.models import PipelineRunRow
            from sqlalchemy import select, delete
            row = db.execute(select(PipelineRunRow).filter(PipelineRunRow.run_id == run_id)).scalar_one_or_none()
            if row:
                db.execute(delete(PipelineRunRow).filter(PipelineRunRow.run_id == run_id))
                db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"DBRunStore delete_run failed for {run_id}: {e}")
            db.rollback()
            return False
        finally:
            db.close()

    def delete_all_runs(self, user_id: int | None = None) -> int:
        db = self._get_db()
        try:
            from backend.app.db.models import PipelineRunRow
            from sqlalchemy import delete
            stmt = delete(PipelineRunRow)
            if user_id is not None:
                stmt = stmt.filter(PipelineRunRow.user_id == user_id)
            result = db.execute(stmt)
            db.commit()
            return result.rowcount
        except Exception as e:
            logger.error(f"DBRunStore delete_all_runs failed: {e}")
            db.rollback()
            return 0
        finally:
            db.close()

def get_run_store() -> RunStore:
    db_url = settings.DATABASE_URL
    if db_url and "postgres" in db_url.lower() and settings.DB_ENABLED:
        return DBRunStore()
    return LocalRunStore()
