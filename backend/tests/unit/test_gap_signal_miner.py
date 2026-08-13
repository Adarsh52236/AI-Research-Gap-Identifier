"""Tests for gap signal miner."""
from backend.app.core.gap_analyzer.gap_signal_miner import GapSignalMiner

def test_gap_signal_miner():
    sections = {
        "FUTURE WORK": "This is a sentence. Future work includes testing with more data.",
        "CONCLUSION": "In conclusion, this remains an open problem.",
        "full_text": "Random text."
    }
    
    miner = GapSignalMiner()
    signals = miner.mine_from_sections("paper_123", sections, source="arxiv", year=2024, include_sections=None, top_k=5)
    
    assert len(signals) == 2
    # The FUTURE WORK signal should have higher score due to +0.5 bonus
    assert signals[0].section == "FUTURE WORK"
    assert signals[0].pattern == "future_work"
    assert signals[1].section == "CONCLUSION"
    assert signals[1].pattern == "open_problem"
