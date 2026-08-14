from backend.app.core.eval.groundedness import validate_report_groundedness, _compute_overlap

def test_compute_overlap():
    summary = "The cat is on the mat."
    evidence = "A fluffy cat is sitting on the blue mat."
    
    # summary tokens: the, cat, is, on, mat (5)
    # evidence tokens: a, fluffy, cat, is, sitting, on, the, blue, mat (9)
    # intersection: the, cat, is, on, mat (5)
    
    score = _compute_overlap(summary, evidence)
    assert score == 1.0
    
    score2 = _compute_overlap("dog runs", "cat walks")
    assert score2 == 0.0

def test_validate_report_groundedness():
    report_json = {
        "gaps": [
            {
                "summary": "Need better evaluation metrics",
                "citations": ["ev1", "ev2"]
            },
            {
                "summary": "Need more data",
                "citations": ["ev3"]
            },
            {
                "summary": "No citations here",
                "citations": []
            }
        ]
    }
    
    evidence_texts = {
        "ev1": "Current evaluation metrics are lacking.",
        "ev2": "We need better evaluation approaches.",
        # ev3 is missing, so it's an invalid citation
    }
    
    res = validate_report_groundedness(report_json, evidence_texts)
    
    assert res["total_gaps"] == 3
    assert res["gaps_without_citations"] == 1
    assert res["missing_citations_count"] == 1
    assert res["invalid_citations_count"] == 1  # ev3
    assert res["all_citations_valid"] is False
    
    # Check overlap proxy
    # gap 1 has "better evaluation" overlap
    assert res["citation_relevance_proxy"] > 0.0
