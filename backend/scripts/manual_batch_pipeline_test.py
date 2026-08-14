"""Manual test script to run the batch pipeline locally."""
import asyncio
import json
import logging
import os
from pathlib import Path
from dotenv import load_dotenv

# Load env before importing settings
base_dir = Path(__file__).parent.parent.parent
env_path = base_dir / "backend" / ".env"
if env_path.exists():
    load_dotenv(env_path)

from backend.app.core.pipeline.pipeline_runner import PipelineRunner
from backend.app.db.schemas import PipelineRunRequest

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    runner = PipelineRunner()
    
    req = PipelineRunRequest(
        query="KV cache optimization long context",
        limit=2,  # Keep limit small for the manual test so it finishes quickly
        steps=["search", "download", "extract", "mine", "index", "report"],
        force_reindex=False,
        force_report=True
    )
    
    print("Starting Batch Pipeline Run...")
    status = await runner.run(req)
    
    print("\n--- PIPELINE RUN STATUS ---")
    print(json.dumps(status.model_dump(), indent=2))
    
    if status.report_path and os.path.exists(status.report_path):
        print("\n--- REPORT OUTPUT ---")
        with open(status.report_path, "r", encoding="utf-8") as f:
            print(f.read())
            
if __name__ == "__main__":
    asyncio.run(main())
