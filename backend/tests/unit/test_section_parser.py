"""Tests for section parser."""
from backend.app.core.extractor.section_parser import SectionParser

def test_parse_sections():
    text = """Some preamble text that nobody reads.
    
1. ABSTRACT
This is the abstract content.

II. INTRODUCTION
This is the introduction.
We talk about things here.

3. METHODOLOGY
Methods go here.

CONCLUSION
Done."""
    parser = SectionParser()
    sections = parser.parse_sections(text)
    
    assert "ABSTRACT" in sections
    assert "This is the abstract content." in sections["ABSTRACT"]
    
    assert "INTRODUCTION" in sections
    assert "This is the introduction." in sections["INTRODUCTION"]
    
    assert "METHODOLOGY" in sections
    assert "CONCLUSION" in sections
    assert "full_text" in sections

def test_infer_abstract_if_missing():
    text = """This is a guess at the abstract because it comes before the intro.
    
INTRODUCTION
We start here."""
    parser = SectionParser()
    sections = parser.parse_sections(text)
    
    assert "INTRODUCTION" in sections
    assert "ABSTRACT" in sections
    assert "guess at the abstract" in sections["ABSTRACT"]
