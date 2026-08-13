"""Text cleaner for raw extracted text."""
import re

def clean_text(text: str) -> str:
    """Cleans up raw PDF text while being conservative to avoid losing meaning."""
    if not text:
        return ""
        
    # 1. Normalize line endings
    t = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # 2. Fix hyphenation across line breaks (e.g. "exam-\nple" -> "example")
    t = re.sub(r'([a-zA-Z])-\n([a-zA-Z])', r'\1\2', t)
    
    # 3. Join lines that are broken mid-sentence.
    # If a line doesn't end with punctuation and next line starts with a lowercase letter, join them.
    t = re.sub(r'([^.!?\n:-])\n([a-z])', r'\1 \2', t)
    
    # 4. Remove excessive consecutive blank lines (limit to max 2)
    t = re.sub(r'\n{3,}', '\n\n', t)
    
    # 5. Collapse excessive spaces
    t = re.sub(r'[ \t]+', ' ', t)
    
    return t.strip()
