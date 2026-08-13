"""Tests for gap patterns."""
from backend.app.core.nlp.gap_patterns import match_gap_patterns

def test_gap_patterns_match():
    hits = match_gap_patterns("Future work includes better metrics.")
    assert len(hits) == 1
    assert hits[0][0] == "future_work"
    
    hits2 = match_gap_patterns("This remains an open problem in the field.")
    assert hits2[0][0] == "open_problem"
    
    hits3 = match_gap_patterns("This topic has not been explored properly.")
    assert hits3[0][0] == "not_explored"
