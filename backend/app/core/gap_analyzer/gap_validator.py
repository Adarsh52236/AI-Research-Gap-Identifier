"""Gap Report Validator."""
from backend.app.db.schemas import GapReport

def validate_gap_report(report: GapReport, evidence_ids: set[str]) -> list[str]:
    problems = []
    
    for i, gap in enumerate(report.gaps):
        if not gap.citations:
            problems.append(f"Gap '{gap.title}' has no citations.")
        else:
            for c in gap.citations:
                if c not in evidence_ids:
                    problems.append(f"Gap '{gap.title}' cited an unknown evidence_id: {c}")
                    
        if not (0.0 <= gap.confidence <= 1.0):
            problems.append(f"Gap '{gap.title}' has invalid confidence: {gap.confidence}")
            
    return problems
