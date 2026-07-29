from dataclasses import dataclass
from typing import List

@dataclass
class IndexingResult:
    """Represents the outcome of a paper indexing operation."""
    total_papers: int
    indexed_papers: int
    failed_papers: int
    indexed_ids: List[str]
    failed_ids: List[str]
