import pytest
import os
import uuid
from datetime import datetime
from backend.app.core.pipeline.run_store import DBRunStore, LocalRunStore, get_run_store
from backend.app.db.schemas import PipelineRunStatus
from backend.app.db.session import SessionLocal, engine
from backend.app.db.models import Base, PipelineRunRow

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup runs created during tests
    db = SessionLocal()
    from backend.app.db.models import ReportRow
    db.query(ReportRow).delete()
    db.query(PipelineRunRow).delete()
    db.commit()
    db.close()

def test_dbrunstore_create_and_get():
    store = DBRunStore()
    run_id = f"test_run_{uuid.uuid4().hex[:8]}"
    
    status = PipelineRunStatus(
        run_id=run_id,
        status="pending",
        query="test query",
        steps=["search"],
        started_at=datetime.utcnow().isoformat()
    )
    
    # Test Create
    store.create_run(status)
    
    # Test Get
    retrieved = store.get_run(run_id)
    assert retrieved is not None
    assert retrieved.run_id == run_id
    assert retrieved.status == "pending"
    assert retrieved.query == "test query"

def test_dbrunstore_update():
    store = DBRunStore()
    run_id = f"test_run_{uuid.uuid4().hex[:8]}"
    
    status = PipelineRunStatus(
        run_id=run_id,
        status="running",
        query="test update",
        steps=["search", "download"],
        started_at=datetime.utcnow().isoformat()
    )
    store.create_run(status)
    
    # Update fields
    status.status = "completed"
    status.papers_found = 10
    store.update_run(run_id, status)
    
    retrieved = store.get_run(run_id)
    assert retrieved.status == "completed"
    assert retrieved.papers_found == 10

def test_dbrunstore_append_event():
    store = DBRunStore()
    run_id = f"test_run_{uuid.uuid4().hex[:8]}"
    
    status = PipelineRunStatus(
        run_id=run_id,
        status="running",
        query="test events",
        steps=["search"],
        started_at=datetime.utcnow().isoformat()
    )
    store.create_run(status)
    
    event1 = {"ts": datetime.utcnow().isoformat(), "step": "search", "msg": "started"}
    store.append_event(run_id, event1)
    
    # Verify in DB
    db = SessionLocal()
    row = db.query(PipelineRunRow).filter_by(run_id=run_id).first()
    assert row is not None
    assert "started" in row.events_json
    db.close()

def test_get_run_store_factory(monkeypatch):
    monkeypatch.setattr("backend.app.config.settings.DATABASE_URL", "postgresql://user:pass@localhost/db")
    monkeypatch.setattr("backend.app.config.settings.DB_ENABLED", True)
    store = get_run_store()
    assert isinstance(store, DBRunStore)
    
    monkeypatch.setattr("backend.app.config.settings.DATABASE_URL", "sqlite:///./test.db")
    store = get_run_store()
    assert isinstance(store, LocalRunStore)
