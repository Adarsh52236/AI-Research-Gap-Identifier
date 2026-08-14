import sys
import json
from pathlib import Path
from backend.app.core.eval.groundedness import validate_report_groundedness
from backend.app.core.eval.metrics import inter_annotator_agreement_simple

def main():
    if len(sys.argv) < 3:
        print("Usage: python backend/scripts/eval_gap_reports.py <report_json_path> <evidence_texts_json_path> [labels_json_path]")
        sys.exit(1)
        
    report_path = Path(sys.argv[1])
    evidence_path = Path(sys.argv[2])
    labels_path = Path(sys.argv[3]) if len(sys.argv) > 3 else None
    
    with open(report_path) as f:
        report = json.load(f)
        
    with open(evidence_path) as f:
        evidence_texts = json.load(f)
        
    print(f"Evaluating Report: {report_path.name}")
    
    metrics = validate_report_groundedness(report, evidence_texts)
    
    print("-" * 40)
    print("Groundedness Metrics:")
    print(f"Total Gaps: {metrics['total_gaps']}")
    print(f"All Citations Valid: {metrics['all_citations_valid']}")
    print(f"Invalid Citations: {metrics['invalid_citations_count']}")
    print(f"Missing Citations: {metrics['missing_citations_count']}")
    print(f"Gaps w/o Citations: {metrics['gaps_without_citations']}")
    print(f"Citation Relevance Proxy (overlap): {metrics['citation_relevance_proxy']:.2f}")
    
    if labels_path and labels_path.exists():
        with open(labels_path) as f:
            labels_doc = json.load(f)
            
        print("-" * 40)
        print("Human Agreement Metrics:")
        # We assume run_id or report name maps directly, for simplicity we just grab report_labels
        report_labels = labels_doc.get("report_labels", [])
        grounded_labels = {lbl["gap_id"]: lbl["is_grounded"] for lbl in report_labels if "is_grounded" in lbl}
        useful_labels = {lbl["gap_id"]: lbl["is_useful"] for lbl in report_labels if "is_useful" in lbl}
        
        # A mock system output where we just say everything is grounded/useful
        sys_grounded = {k: True for k in grounded_labels.keys()}
        sys_useful = {k: True for k in useful_labels.keys()}
        
        g_agr = inter_annotator_agreement_simple(sys_grounded, grounded_labels)
        u_agr = inter_annotator_agreement_simple(sys_useful, useful_labels)
        
        print(f"Grounded Agreement: {g_agr['agreement']:.2f} (n={g_agr['total_common']})")
        print(f"Useful Agreement: {u_agr['agreement']:.2f} (n={u_agr['total_common']})")

if __name__ == "__main__":
    main()
