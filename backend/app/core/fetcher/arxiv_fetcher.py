"""arXiv fetcher."""
import httpx
import xml.etree.ElementTree as ET
from typing import List, Optional
from backend.app.core.fetcher.base_fetcher import BaseFetcher
from backend.app.db.schemas import PaperMetadata, PaperAuthor
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)

class ArxivFetcher(BaseFetcher):
    """Fetches papers from arXiv."""
    
    @property
    def source_name(self) -> str:
        return "arxiv"

    async def search(self, query: str, limit: int, year_from: Optional[int] = None, year_to: Optional[int] = None) -> List[PaperMetadata]:
        url = f"https://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={limit}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()
        except Exception as e:
            logger.error(f"Error fetching from ArXiv: {e}")
            return []

        try:
            root = ET.fromstring(response.text)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            
            papers = []
            for entry in root.findall("atom:entry", ns):
                title = entry.find("atom:title", ns).text
                if title:
                    title = title.replace("\n", " ").strip()
                
                abstract = entry.find("atom:summary", ns)
                abstract_text = abstract.text.replace("\n", " ").strip() if abstract is not None and abstract.text else None
                
                authors = []
                for author in entry.findall("atom:author", ns):
                    name = author.find("atom:name", ns)
                    if name is not None:
                        authors.append(PaperAuthor(name=name.text))
                
                published = entry.find("atom:published", ns)
                year = None
                if published is not None and published.text:
                    year = int(published.text[:4])
                    if year_from and year < year_from:
                        continue
                    if year_to and year > year_to:
                        continue

                entry_id = entry.find("atom:id", ns)
                paper_url = entry_id.text if entry_id is not None else None
                
                pdf_url = None
                for link in entry.findall("atom:link", ns):
                    if link.attrib.get("title") == "pdf" or link.attrib.get("rel") == "related":
                        href = link.attrib.get("href")
                        if href and "pdf" in href:
                            pdf_url = href
                            break
                            
                paper_id = paper_url.split("/")[-1] if paper_url else str(hash(f"{title}{year}arxiv"))
                
                paper = PaperMetadata(
                    paper_id=paper_id,
                    title=title or "Untitled",
                    abstract=abstract_text,
                    authors=authors,
                    year=year,
                    source=self.source_name,
                    url=paper_url,
                    pdf_url=pdf_url,
                    doi=None
                )
                papers.append(paper)
            return papers
        except Exception as e:
            logger.error(f"Error parsing ArXiv XML: {e}")
            return []
