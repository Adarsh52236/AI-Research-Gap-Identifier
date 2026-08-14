"""Tests for gap noise filter."""
from backend.app.core.gap_analyzer.gap_signal_miner import is_noise_sentence, compute_alpha_ratio, looks_like_caption_or_table

def test_compute_alpha_ratio():
    assert compute_alpha_ratio("abc") == 1.0
    assert compute_alpha_ratio("abc 123") < 1.0
    assert compute_alpha_ratio("12345") == 0.0

def test_looks_like_caption_or_table():
    assert looks_like_caption_or_table("Table 1: Results on dataset...") == True
    assert looks_like_caption_or_table("Figure 2 shows the architecture.") == True
    assert looks_like_caption_or_table("This is a normal sentence about future work.") == False
    assert looks_like_caption_or_table("Smith et al. 2023 2024 10 20 30") == True # et al + numbers
    assert looks_like_caption_or_table("12") == True # page number
    assert looks_like_caption_or_table("1 2 3 4 5 6 7 8 9") == True # high digit ratio

def test_is_noise_sentence():
    # Short sentence
    assert is_noise_sentence("Too short.") == True
    
    # Low alpha
    assert is_noise_sentence("123 456 789 012 345 678 901 234 567 890") == True
    
    # Repeated chars
    assert is_noise_sentence("IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII") == True
    
    # Citation artifacts
    assert is_noise_sentence("[1] [2] [3] [4] [5] [6]") == True
    
    # Valid gap sentence
    assert is_noise_sentence("However, this remains an open problem for future work to address comprehensively.") == False
