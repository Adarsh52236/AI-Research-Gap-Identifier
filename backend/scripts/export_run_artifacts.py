"""
Export Run Artifacts

Usage:
  python backend/scripts/export_run_artifacts.py <run_id>

Bundles the artifacts of a specific pipeline run into `storage/exports/<run_id>/`
for easy sharing or attachment to research papers as supplementary material.
"""

import sys
import shutil
import argparse
from pathlib import Path

def export_run(run_id: str):
    base_dir = Path("storage")
    run_dir = base_dir / "runs" / run_id
    export_dir = base_dir / "exports" / run_id
    
    if not run_dir.exists():
        print(f"Error: Run directory not found: {run_dir}")
        sys.exit(1)
        
    # Create export directory
    export_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Copy run status and events
    status_file = run_dir / "status.json"
    events_file = run_dir / "events.jsonl"
    if status_file.exists():
        shutil.copy2(status_file, export_dir / "status.json")
        print(f"Copied status.json")
    if events_file.exists():
        shutil.copy2(events_file, export_dir / "events.jsonl")
        print(f"Copied events.jsonl")
        
    # 2. Copy report if exists
    report_file = base_dir / "reports" / f"report_{run_id}.md"
    if report_file.exists():
        shutil.copy2(report_file, export_dir / "report.md")
        print(f"Copied report.md")
        
    # 3. Create a config snapshot (just copy .env template or config.py)
    config_dest = export_dir / "config_snapshot.py"
    config_src = Path("backend/app/config.py")
    if config_src.exists():
        shutil.copy2(config_src, config_dest)
        print("Copied config snapshot.")
        
    # 4. (Optional) Zip it up
    zip_path = base_dir / "exports" / f"{run_id}_artifacts"
    shutil.make_archive(str(zip_path), 'zip', str(export_dir))
    print(f"\nExport complete! Artifacts zipped at: {zip_path}.zip")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export artifacts for a pipeline run.")
    parser.add_argument("run_id", help="The UUID of the pipeline run.")
    args = parser.parse_args()
    
    export_run(args.run_id)
