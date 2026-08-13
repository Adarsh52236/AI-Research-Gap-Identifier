"""Semantic Scholar fetcher."""
import httpx
import os
from typing import List, Optional
from backend.app.core.fetcher.base_fetcher import BaseFetcher
from backend.app.db.schemas import PaperMetadata, PaperAuthor
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)

class SemanticScholarFetcher(BaseFetcher):
    """Fetches papers from Semantic Scholar."""
    
    @property
    def source_name(self) -> str:
        return "semantic_scholar"

    async def search(self, query: str, limit: int, year_from: Optional[int] = None, year_to: Optional[int] = None) -> List[PaperMetadata]:
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        params = {
            "query": query,
            "limit": limit,
            "fields": "title,abstract,authors,year,url,externalIds,openAccessPdf"
        }
        
        headers = {}
        api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
        if api_key:
            headers["x-api-key"] = api_key
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                data = response.json()
        except Exception as e:
            logger.error(f"Error fetching from Semantic Scholar: {e}")
            return []
            
        papers = []
        for item in data.get("data", []):
            year = item.get("year")
            if year:
                if year_from and year < year_from:
                    continue
                if year_to and year > year_to:
                    continue
                    
            title = item.get("title", "Untitled")
            abstract = item.get("abstract")
            url_link = item.get("url")
            
            authors = []
            for author in item.get("authors", []):
                if author.get("name"):
                    authors.append(PaperAuthor(name=author["name"]))
                    
            external_ids = item.get("externalIds", {})
            doi = external_ids.get("DOI")
            
            pdf_url = None
            oa_pdf = item.get("openAccessPdf")
            if oa_pdf and oa_pdf.get("url"):
                pdf_url = oa_pdf["url"]
                
            paper_id = item.get("paperId") or str(hash(f"{title}{year}semantic_scholar"))
            
            papers.append(PaperMetadata(
                paper_id=paper_id,
                title=title,
                abstract=abstract,
                authors=authors,
                year=year,
                source=self.source_name,
                url=url_link,
                pdf_url=pdf_url,
                doi=doi
            ))
            
        return papers
