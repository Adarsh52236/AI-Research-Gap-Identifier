import re
from backend.app.db.schemas import ReviewLLMOutput

def normalize_text(text: str) -> str:
    """Normalize whitespace for fuzzy matching."""
    return re.sub(r'\s+', ' ', text).strip().lower()

def validate_and_filter_issues(llm_output: ReviewLLMOutput, extracted_text: str) -> tuple[ReviewLLMOutput, int]:
    """
    Validates that the evidence (anchor and quote) actually exists in the extracted text.
    Returns the filtered ReviewLLMOutput and the number of dropped issues.
    """
    normalized_full_text = normalize_text(extracted_text)
    
    valid_issues = []
    dropped_count = 0
    
    for issue in llm_output.issues:
        anchor = issue.evidence.anchor_phrase
        quote = issue.evidence.quote
        
        # Check if anchor exists
        normalized_anchor = normalize_text(anchor)
        anchor_found = normalized_anchor in normalized_full_text
        
        # Check if quote exists (if provided)
        quote_found = True
        if quote:
            normalized_quote = normalize_text(quote)
            quote_found = normalized_quote in normalized_full_text
            
        if anchor_found and quote_found:
            valid_issues.append(issue)
        else:
            dropped_count += 1
            
    llm_output.issues = valid_issues
    return llm_output, dropped_count
