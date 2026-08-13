"""Simple heuristic sentence splitter."""
import re

def split_sentences(text: str) -> list[str]:
    """Splits a paragraph into sentences using regex heuristics."""
    if not text:
        return []
    
    # Split on .?! followed by whitespace and a capital letter.
    # We use a lookbehind for the punctuation and lookahead for the capital letter.
    # Note: Regex doesn't easily support variable length lookbehinds, so we split and re-attach.
    # A simpler approach: split by (?<=[.?!])\s+(?=[A-Z])
    sentences = re.split(r'(?<=[.?!])\s+(?=[A-Z])', text)
    
    cleaned = []
    for s in sentences:
        s = s.strip()
        # Filter out very short fragments
        if len(s) >= 20:
            cleaned.append(s)
            
    return cleaned
