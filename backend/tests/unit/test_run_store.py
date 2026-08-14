import os
import json
from datetime import datetime
from backend.app.core.pipeline.run_store import RunStore
from backend.app.db.schemas import PipelineRunStatus

def test_run_store(tmp_path, monkeypatch):
    from backend.app.config import settings
    monkeypatch.setattr(settings, "RUNS_DIR", str(tmp_path / "runs"))
    
    store = RunStore()
    run_id = "test_run_123"
    
    status = PipelineRunStatus(
        run_id=run_id,
        status="running",
        started_at=datetime.utcnow().isoformat(),
        query="test query",
        steps=["search"]
    )
    
    store.save_status(run_id, status)
    loaded = store.load_status(run_id)
    assert loaded is not None
    assert loaded.run_id == run_id
    assert loaded.status == "running"
    
    store.append_event(run_id, {"event": "hello"})
    events_path = tmp_path / "runs" / run_id / "events.jsonl"
    assert events_path.exists()
    
    with open(events_path, "r") as f:
        data = json.loads(f.read().strip())
        assert data["event"] == "hello"
