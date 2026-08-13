"""Base fetcher."""
from typing import List, Optional
from abc import ABC, abstractmethod
from backend.app.db.schemas import PaperMetadata

class BaseFetcher(ABC):
    """Base class for paper fetchers."""
    
    @property
    @abstractmethod
    def source_name(self) -> str:
        pass
        
    @abstractmethod
    async def search(self, query: str, limit: int, year_from: Optional[int] = None, year_to: Optional[int] = None) -> List[PaperMetadata]:
        pass
