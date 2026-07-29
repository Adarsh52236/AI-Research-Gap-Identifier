from typing import List
from app.services.ingestion.models import Paper
from .base import EmbeddingProvider
from .models import EmbeddingResult
from app.core.logging import logger

class EmbeddingService:
    """Service for handling paper embedding operations utilizing dependency injection."""
    
    def __init__(self, provider: EmbeddingProvider):
        """
        Accepts an EmbeddingProvider dependency, decoupling the service from specific
        implementations (like Sentence Transformers vs OpenAI).
        """
        self.provider = provider
        
    def _format_paper(self, paper: Paper) -> str:
        """Combines title and abstract into a single formatted string."""
        return f"Title: {paper.title}\n\nAbstract:\n{paper.abstract}"

    def embed_paper(self, paper: Paper) -> EmbeddingResult:
        """Generates an embedding for a single Paper object."""
        logger.info(f"Embedding paper: '{paper.title}'")
        formatted_text = self._format_paper(paper)
        return self.provider.embed(formatted_text)
        
    def embed_papers(self, papers: List[Paper]) -> List[EmbeddingResult]:
        """Generates embeddings for a batch of Paper objects."""
        logger.info(f"Embedding batch of {len(papers)} papers.")
        formatted_texts = [self._format_paper(p) for p in papers]
        return self.provider.embed_batch(formatted_texts)
