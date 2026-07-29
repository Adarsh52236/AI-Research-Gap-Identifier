from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass
class EmbeddingResult:
    """Represents the output of an embedding operation."""
    vector: List[float]
    dimensions: int
    model_name: str
    provider_name: str
    created_at: datetime
