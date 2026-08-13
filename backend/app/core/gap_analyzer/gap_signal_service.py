"""Gap Signal Service."""
import json
import time
from pathlib import Path
from collections import defaultdict
from fastapi import HTTPException
from backend.app.config import settings
from backend.app.db.schemas import MineGapSignalsResponse, GapSignal
from backend.app.core.gap_analyzer.gap_signal_miner import GapSignalMiner
from backend.app.utils.file_utils import safe_resolve_under, ensure_dir
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)

class GapSignalService:
    def __init__(self):
        self.miner = GapSignalMiner()
        
    def process_mining_request(self, paper_ids: list[str] | None, processed_sections_paths: list[str] | None,
                               top_k: int, include_sections: list[str] | None, save: bool) -> MineGapSignalsResponse:
        
        base_dir = Path(settings.STORAGE_DIR)
        sections_to_process = []
        
        # Resolve paths
        if paper_ids:
            for pid in paper_ids:
                rel_path = f"processed/{pid}/sections.json"
                try:
                    p = safe_resolve_under(base_dir, rel_path)
                    sections_to_process.append((pid, p))
                except ValueError:
                    continue
                    
        if processed_sections_paths:
            for r_path in processed_sections_paths:
                try:
                    p = safe_resolve_under(base_dir, r_path)
                    # Extract paper_id from path assumption: processed/<pid>/sections.json
                    pid = p.parent.name
                    sections_to_process.append((pid, p))
                except ValueError:
                    continue
                    
        if not sections_to_process:
            raise HTTPException(status_code=400, detail="No valid paper_ids or paths provided.")
            
        all_signals = []
        
        for pid, path in sections_to_process:
            if not path.exists():
                logger.warning(f"Sections file missing for {pid}: {path}")
                raise HTTPException(status_code=404, detail=f"Sections not found for {pid}")
                
            try:
                with open(path, "r", encoding="utf-8") as f:
                    sections_data = json.load(f)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to read JSON for {pid}: {e}")
                
            signals = self.miner.mine_from_sections(
                paper_id=pid,
                sections=sections_data,
                source=None,
                year=None,
                include_sections=include_sections,
                top_k=top_k
            )
            all_signals.extend(signals)
            
        # Aggregate and boost
        pattern_counts = defaultdict(int)
        for sig in all_signals:
            pattern_counts[sig.pattern] += 1
            
        for sig in all_signals:
            if pattern_counts[sig.pattern] >= 3:
                sig.score += 0.2
                sig.score = round(sig.score, 2)
                
        # Final sort across all papers
        all_signals.sort(key=lambda x: (x.score, len(x.sentence)), reverse=True)
        top_signals = all_signals[:top_k]
        
        results_path = None
        if save and top_signals:
            ts = int(time.time())
            if len(sections_to_process) == 1:
                pid = sections_to_process[0][0]
                save_dir = Path(settings.PROCESSED_DIR) / pid
            else:
                save_dir = Path(settings.PROCESSED_DIR) / f"batch_{ts}"
                
            ensure_dir(save_dir)
            out_file = save_dir / "gap_signals.json"
            
            out_data = [s.model_dump() for s in top_signals]
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(out_data, f, indent=2, ensure_ascii=False)
                
            results_path = out_file.as_posix()
            
        return MineGapSignalsResponse(
            status="mined",
            count=len(top_signals),
            results_path=results_path,
            signals=top_signals
        )
