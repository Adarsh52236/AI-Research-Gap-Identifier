import re

def _compute_overlap(summary: str, evidence: str) -> float:
    """
    Computes a simple token overlap ratio between summary and evidence.
    Returns the percentage of unique words in summary that appear in the evidence.
    """
    if not summary or not evidence:
        return 0.0
        
    # lower and tokenize
    summary_tokens = set(re.findall(r'\w+', summary.lower()))
    evidence_tokens = set(re.findall(r'\w+', evidence.lower()))
    
    if not summary_tokens:
        return 0.0
        
    overlap = summary_tokens.intersection(evidence_tokens)
    return len(overlap) / len(summary_tokens)

def validate_report_groundedness(report_json: dict, evidence_texts: dict[str, str]) -> dict:
    """
    Validates groundedness of a GapReport.
    
    Args:
        report_json (dict): The serialized GapReport.
        evidence_texts (dict): Map of evidence_id -> text content for all provided evidence.
        
    Returns:
        dict containing validation metrics.
    """
    evidence_ids = set(evidence_texts.keys())
    
    total_gaps = len(report_json.get("gaps", []))
    missing_citations_count = 0
    invalid_citations_count = 0
    gaps_without_citations = 0
    overlap_scores = []
    
    for gap in report_json.get("gaps", []):
        citations = gap.get("citations", [])
        if not citations:
            gaps_without_citations += 1
            missing_citations_count += 1
            overlap_scores.append(0.0)
            continue
            
        gap_summary = gap.get("summary", "")
        best_overlap_for_gap = 0.0
        
        for citation in citations:
            if citation not in evidence_ids:
                invalid_citations_count += 1
            else:
                # compute heuristic relevance proxy
                evidence_text = evidence_texts[citation]
                overlap = _compute_overlap(gap_summary, evidence_text)
                best_overlap_for_gap = max(best_overlap_for_gap, overlap)
                
        overlap_scores.append(best_overlap_for_gap)
                
    avg_overlap = sum(overlap_scores) / len(overlap_scores) if overlap_scores else 0.0
    
    return {
        "all_citations_valid": invalid_citations_count == 0,
        "missing_citations_count": missing_citations_count,
        "invalid_citations_count": invalid_citations_count,
        "gaps_without_citations": gaps_without_citations,
        "total_gaps": total_gaps,
        "citation_relevance_proxy": avg_overlap
    }
