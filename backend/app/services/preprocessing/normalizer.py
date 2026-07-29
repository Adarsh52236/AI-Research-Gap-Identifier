from dataclasses import replace
from app.services.ingestion.models import Paper
from app.services.preprocessing.text_cleaner import clean_and_normalize_text
from app.core.logging import logger

def normalize_paper(paper: Paper) -> Paper:
    """
    Applies text cleaning and normalization to the fields of a Paper object.
    Returns a new Paper instance with normalized fields to ensure immutability.
    """
    new_title = clean_and_normalize_text(paper.title)
    new_abstract = clean_and_normalize_text(paper.abstract)
    
    normalized_authors = []
    for author in paper.authors:
        cleaned = clean_and_normalize_text(author)
        if cleaned:
            normalized_authors.append(cleaned)
            
    normalized_categories = []
    for category in paper.categories:
        cleaned = clean_and_normalize_text(category)
        if cleaned:
            normalized_categories.append(cleaned)
            
    normalized_paper = replace(
        paper,
        title=new_title,
        abstract=new_abstract,
        authors=normalized_authors,
        categories=normalized_categories
    )
    
    logger.info("Normalization completion successful.")
    return normalized_paper
