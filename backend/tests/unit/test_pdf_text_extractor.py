"""Test PDF text extractor and cleaner."""
import fitz
from backend.app.core.extractor.pdf_extractor import PDFTextExtractor
from backend.app.core.extractor.text_cleaner import clean_text

def test_pdf_extraction_and_cleaning(tmp_path):
    pdf_path = tmp_path / "test.pdf"
    
    # Create a tiny PDF
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(fitz.Point(50, 50), "ABSTRACT")
    page.insert_text(fitz.Point(50, 100), "Hello world. This is a line break that ")
    page.insert_text(fitz.Point(50, 120), "hyphens a word: exam-")
    page.insert_text(fitz.Point(50, 140), "ple.")
    page.insert_text(fitz.Point(50, 200), "INTRODUCTION")
    page.insert_text(fitz.Point(50, 250), "Done.")
    doc.save(pdf_path)
    doc.close()
    
    extractor = PDFTextExtractor()
    raw_text = extractor.extract_text(pdf_path)
    
    assert "ABSTRACT" in raw_text
    assert "exam-" in raw_text
    
    cleaned = clean_text(raw_text)
    assert "example" in cleaned  # de-hyphenated
    assert "Hello world." in cleaned
