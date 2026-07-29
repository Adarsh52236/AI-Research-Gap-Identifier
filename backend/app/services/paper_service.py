from typing import List
from app.services.ingestion.arxiv import ArxivSource
from app.services.ingestion.models import Paper
from app.services.ingestion.exceptions import PaperFetchError, PaperParseError
from app.core.logging import logger

class PaperService:
    def __init__(self):
        # Instantiate ArxivSource internally
        self.arxiv_source = ArxivSource()

    def search_papers(self, query: str, max_results: int = 10) -> List[Paper]:
        """
        Search for papers using the underlying sources (currently only arXiv).
        """
        try:
            return self.arxiv_source.search(query=query, max_results=max_results)
        except PaperFetchError as e:
            logger.error(f"PaperFetchError in PaperService: {e}")
            raise
        except PaperParseError as e:
            logger.error(f"PaperParseError in PaperService: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in PaperService search_papers: {e}")
            raise
