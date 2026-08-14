import sys
import json
from pathlib import Path
from backend.app.core.eval.metrics import precision_at_k

def main():
    if len(sys.argv) < 3:
        print("Usage: python backend/scripts/eval_gap_signals.py <dataset_json> <labels_json>")
        sys.exit(1)
        
    dataset_path = Path(sys.argv[1])
    labels_path = Path(sys.argv[2])
    
    with open(dataset_path) as f:
        dataset = json.load(f)
        
    with open(labels_path) as f:
        labels_doc = json.load(f)
        
    # Build truth map: paper_id -> set of signal_ids that are true gaps
    truth_map = {}
    for lbl in labels_doc.get("labels", []):
        if lbl.get("is_true_gap_statement"):
            paper_id = lbl["paper_id"]
            if paper_id not in truth_map:
                truth_map[paper_id] = set()
            truth_map[paper_id].add(lbl["signal_id"])
            
    print(f"Evaluating dataset: {dataset['dataset_name']}")
    
    total_p10 = 0.0
    total_p20 = 0.0
    evaluated_papers = 0
    
    for paper in dataset.get("papers", []):
        paper_id = paper["paper_id"]
        signals_path = Path(paper["gap_signals_path"])
        
        if not signals_path.exists():
            print(f"[{paper_id}] WARN: signals path not found: {signals_path}")
            continue
            
        with open(signals_path) as f:
            signals = json.load(f)
            
        # Sort signals by score descending
        signals.sort(key=lambda x: x.get("score", 0.0), reverse=True)
        predicted_ids = [s["signal_id"] for s in signals]
        true_ids = truth_map.get(paper_id, set())
        
        p10 = precision_at_k(predicted_ids, true_ids, 10)
        p20 = precision_at_k(predicted_ids, true_ids, 20)
        
        print(f"[{paper_id}] P@10: {p10:.2f} | P@20: {p20:.2f} (True gaps labeled: {len(true_ids)})")
        
        total_p10 += p10
        total_p20 += p20
        evaluated_papers += 1
        
    if evaluated_papers > 0:
        print("-" * 40)
        print(f"Average P@10: {total_p10/evaluated_papers:.2f}")
        print(f"Average P@20: {total_p20/evaluated_papers:.2f}")
    else:
        print("No papers evaluated.")

if __name__ == "__main__":
    main()
