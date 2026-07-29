from typing import Dict, Any
from app.services.ingestion.models import Paper

class PaperMetadataMapper:
    """Maps a Paper object to a vector store metadata dictionary."""
    
    @staticmethod
    def map_to_metadata(paper: Paper) -> Dict[str, Any]:
        """
        Converts a Paper object into a flat dictionary suitable for ChromaDB.
        Chroma metadata supports only scalar values (str, int, float, bool).
        """
        metadata = {
            "title": paper.title,
            "source": paper.source,
            "published_date": paper.published_date.isoformat() if paper.published_date else "",
            "authors": ", ".join(paper.authors) if paper.authors else "",
            "categories": ", ".join(paper.categories) if paper.categories else ""
        }
        if paper.doi:
            metadata["doi"] = paper.doi
            
        return metadata
