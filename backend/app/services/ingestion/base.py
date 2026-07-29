from abc import ABC, abstractmethod
from typing import List
from .models import Paper

class PaperSource(ABC):
    @abstractmethod
    def search(self, query: str, max_results: int) -> List[Paper]:
        """Search for papers matching the query."""
        pass
        
    @abstractmethod
    def get_paper(self, paper_id: str) -> Paper:
        """Fetch a specific paper by ID."""
        pass
