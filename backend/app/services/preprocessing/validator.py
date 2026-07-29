from dataclasses import replace
from app.services.ingestion.models import Paper
from app.core.logging import logger

class ValidationError(Exception):
    """Exception raised for validation errors in Paper objects."""
    pass

def validate_paper(paper: Paper) -> Paper:
    """
    Validates a Paper object to ensure critical fields are present.
    Raises ValidationError if validation fails.
    Returns a new Paper instance to enforce immutability across all stages.
    """
    missing_fields = []
    
    if not paper.title or not paper.title.strip():
        missing_fields.append("title")
        
    if not paper.abstract or not paper.abstract.strip():
        missing_fields.append("abstract")
        
    valid_authors = [a for a in paper.authors if a and a.strip()]
    if not paper.authors or not valid_authors:
        missing_fields.append("authors")
        
    if not paper.published_date:
        missing_fields.append("published_date")
        
    if missing_fields:
        error_msg = f"Missing required fields: {', '.join(missing_fields)}"
        logger.error(f"Paper validation failure: {error_msg}")
        raise ValidationError(error_msg)
        
    logger.info("Paper validation success.")
    return replace(paper)
