import re
from datetime import datetime, UTC
from typing import List
import httpx
import feedparser

from app.core.logging import logger
from .base import PaperSource
from .models import Paper
from .exceptions import PaperFetchError, PaperParseError

def clean_text(text: str) -> str:
    """Removes extra whitespace and newlines to return normalized text."""
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

class ArxivSource(PaperSource):
    BASE_URL = "https://export.arxiv.org/api/query"

    def search(self, query: str, max_results: int = 10) -> List[Paper]:
        logger.info(f"Starting arXiv search for query: '{query}' with max_results: {max_results}")
        
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results,
        }
        
        headers = {
            "User-Agent": "AI-Research-Gap-Identifier/0.1"
        }

        try:
            with httpx.Client(timeout=30.0, headers=headers) as client:
                response = client.get(self.BASE_URL, params=params)
                response.raise_for_status()
        except httpx.RequestError as e:
            logger.error(f"HTTP request to arXiv API failed: {e}")
            raise PaperFetchError(f"Request to arXiv API failed: {e}") from e
        except httpx.HTTPStatusError as e:
            logger.error(f"arXiv API returned HTTP error: {e.response.status_code}")
            raise PaperFetchError(f"arXiv API returned HTTP error: {e.response.status_code}") from e

        try:
            feed = feedparser.parse(response.content)
            
            if getattr(feed, "bozo", 0) != 0:
                logger.error(f"Failed to parse arXiv feed: {feed.bozo_exception}")
                raise PaperParseError(f"Failed to parse arXiv feed: {feed.bozo_exception}")
                
            if not feed.entries:
                logger.info("No papers found in arXiv response.")
                return []

            papers = []
            for entry in feed.entries:
                authors = [author.get("name", "Unknown") for author in entry.get("authors", [])]
                categories = [tag.get("term", "") for tag in entry.get("tags", []) if tag.get("term")]
                
                pdf_url = ""
                for link in entry.get("links", []):
                    if link.get("type") == "application/pdf":
                        pdf_url = link.get("href", "")
                        break
                if not pdf_url:
                    pdf_url = entry.get("link", "")

                doi = entry.get("arxiv_doi")

                published_parsed = entry.get("published_parsed")
                if published_parsed:
                    published_date = datetime(*published_parsed[:6], tzinfo=UTC)
                else:
                    published_date = datetime.now(UTC)

                paper = Paper(
                    title=clean_text(entry.get("title", "")),
                    authors=authors,
                    abstract=clean_text(entry.get("summary", "")),
                    published_date=published_date,
                    categories=categories,
                    pdf_url=pdf_url,
                    source="arXiv",
                    doi=doi,
                )
                papers.append(paper)
            
            logger.info(f"Successfully retrieved and parsed {len(papers)} papers from arXiv.")
            return papers
            
        except Exception as e:
            if isinstance(e, PaperParseError):
                raise
            logger.error(f"Unexpected error parsing arXiv response: {e}")
            raise PaperParseError(f"Error parsing arXiv response: {e}") from e

    def get_paper(self, paper_id: str) -> Paper:
        raise NotImplementedError("get_paper is not yet implemented for ArxivSource")
