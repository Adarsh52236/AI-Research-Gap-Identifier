import pymupdf as fitz
from pathlib import Path
from backend.app.core.reviewer.pdf_locator import find_best_rect_for_anchor

def test_find_best_rect():
    # Create a tiny pdf with text
    doc = fitz.open()
    page = doc.new_page()
    test_text = "This is a unique anchor phrase for testing."
    page.insert_text((50, 50), test_text, fontsize=12)
    
    rect = find_best_rect_for_anchor(page, "unique anchor phrase")
    
    assert rect is not None
    assert rect.width > 0
    assert rect.height > 0
    
    # Test not found
    rect_none = find_best_rect_for_anchor(page, "this phrase does not exist")
    assert rect_none is None
