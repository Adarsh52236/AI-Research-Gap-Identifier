from dataclasses import dataclass
from typing import Optional, List, Dict, Any

@dataclass
class SearchResult:
    """Represents a single match returned from a vector store search."""
    score: float
    metadata: Dict[str, Any]
    paper_id: Optional[str] = None
    embedding: Optional[List[float]] = None
