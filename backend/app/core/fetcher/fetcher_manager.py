"""Fetcher manager."""
import re
import asyncio
from typing import List, Optional, Dict
from backend.app.core.fetcher.arxiv_fetcher import ArxivFetcher
from backend.app.core.fetcher.semantic_scholar_fetcher import SemanticScholarFetcher
from backend.app.db.schemas import PaperMetadata
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)

class FetcherManager:
    """Manages multiple fetchers."""
    
    def __init__(self):
        self.fetchers = {
            "arxiv": ArxivFetcher(),
            "semantic_scholar": SemanticScholarFetcher()
        }
        
    def _normalize_title(self, title: str) -> str:
        if not title:
            return ""
        # Lowercase, remove non-alphanumeric, collapse spaces
        s = re.sub(r'[^a-z0-9]', ' ', title.lower())
        return ' '.join(s.split())
        
    def _normalize_doi(self, doi: str) -> str:
        if not doi:
            return ""
        return doi.strip().lower()
        
    def _score_paper(self, paper: PaperMetadata) -> int:
        score = 0
        if paper.abstract: score += 1
        if paper.pdf_url: score += 1
        if paper.doi: score += 1
        return score
        
    def _deduplicate(self, papers: List[PaperMetadata]) -> List[PaperMetadata]:
        deduped = {}
        for paper in papers:
            key = None
            if paper.doi:
                key = f"doi:{self._normalize_doi(paper.doi)}"
            else:
                key = f"title:{self._normalize_title(paper.title)}"
                
            if key in deduped:
                existing = deduped[key]
                if self._score_paper(paper) > self._score_paper(existing):
                    deduped[key] = paper
            else:
                deduped[key] = paper
                
        return list(deduped.values())

    async def search_all(self, query: str, limit: int, sources: List[str], year_from: Optional[int] = None, year_to: Optional[int] = None) -> List[PaperMetadata]:
        tasks = []
        for src in sources:
            if src in self.fetchers:
                tasks.append(self.fetchers[src].search(query, limit, year_from, year_to))
            else:
                logger.warning(f"Unknown source requested: {src}")
                
        if not tasks:
            return []
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_papers = []
        for res in results:
            if isinstance(res, Exception):
                logger.error(f"Error during fetch: {res}")
            elif isinstance(res, list):
                all_papers.extend(res)
                
        return self._deduplicate(all_papers)[:limit]


    @staticmethod
    def build_stable_paper_id(doi: Optional[str], title: Optional[str], year: Optional[int], source: str) -> str:
        """Builds a stable paper ID."""
        import hashlib
        import re
        if doi:
            normalized = doi.strip().lower()
            return hashlib.sha1(normalized.encode('utf-8')).hexdigest()
        else:
            t = title or ""
            t = re.sub(r'[^a-z0-9]', '', t.lower())
            y = str(year) if year else ""
            s = source or ""
            return hashlib.sha256(f"{s}{y}{t}".encode("utf-8")).hexdigest()
