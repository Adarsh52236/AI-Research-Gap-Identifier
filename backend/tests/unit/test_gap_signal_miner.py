"""Tests for gap signal miner."""
from backend.app.core.gap_analyzer.gap_signal_miner import GapSignalMiner

def test_gap_signal_miner():
    sections = {
        "FUTURE WORK": "This is a sentence that is sufficiently long. Future work includes testing with more data.",
        "CONCLUSION": "In conclusion, this remains an open problem for researchers to address completely.",
        "full_text": "Random text that is not a gap at all but long enough to pass."
    }
    
    miner = GapSignalMiner()
    signals = miner.mine_from_sections("paper_123", sections, source="arxiv", year=2024, include_sections=None, top_k=5)
    
    assert len(signals) == 2
    
    # FUTURE WORK should be first because of the +0.5 bonus
    assert signals[0].section == "FUTURE WORK"
    assert signals[0].pattern == "future_work"
    assert signals[1].section == "CONCLUSION"
    assert signals[1].pattern == "open_problem"
    
    assert hasattr(signals[0], "quality_score")
    assert hasattr(signals[0], "is_noise")
    assert not signals[0].is_noise
