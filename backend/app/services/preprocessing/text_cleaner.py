import re
import unicodedata

def clean_and_normalize_text(text: str) -> str:
    """
    Normalizes unicode characters, removes excessive whitespace and newlines,
    and strips surrounding spaces.
    
    Args:
        text (str): The raw input text.
        
    Returns:
        str: The normalized and cleaned text.
    """
    if not text:
        return ""
    
    # Normalize unicode to NFKC form
    text = unicodedata.normalize("NFKC", text)
    
    # Replace newlines, carriage returns, and tabs with spaces
    text = text.replace("\n", " ").replace("\r", " ").replace("\t", " ")
    
    # Remove multiple sequential spaces
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()
