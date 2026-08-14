import json
from pathlib import Path
from backend.app.config import settings
from backend.app.db.schemas import PipelineRunStatus
import os

class RunStore:
    def __init__(self):
        self.runs_dir = Path(settings.RUNS_DIR)
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_run_dir(self, run_id: str) -> Path:
        run_dir = self.runs_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_dir
        
    def save_status(self, run_id: str, status_obj: PipelineRunStatus):
        run_dir = self._get_run_dir(run_id)
        status_path = run_dir / "status.json"
        
        # Write safely
        temp_path = run_dir / "status.json.tmp"
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(status_obj.model_dump_json(indent=2))
        temp_path.replace(status_path)
        
    def load_status(self, run_id: str) -> PipelineRunStatus | None:
        status_path = self._get_run_dir(run_id) / "status.json"
        if not status_path.exists():
            return None
        with open(status_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return PipelineRunStatus(**data)
            
    def append_event(self, run_id: str, event_dict: dict):
        run_dir = self._get_run_dir(run_id)
        events_path = run_dir / "events.jsonl"
        with open(events_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event_dict) + "\n")
