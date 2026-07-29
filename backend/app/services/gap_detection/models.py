from dataclasses import dataclass, field
from typing import List, Dict
from datetime import datetime
from .evidence import EvidenceItem

@dataclass
class ResearchGap:
    """Represents a discovered research gap."""
    id: str
    title: str
    description: str
    confidence: float
    strategy: str
    supporting_topics: List[int]
    evidence: List[EvidenceItem]
    created_at: datetime
    confidence_breakdown: Dict[str, float] = field(default_factory=dict)

@dataclass
class GapDetectionResult:
    """Represents the aggregate result of multiple gap detection strategies."""
    total_gaps: int
    gaps: List[ResearchGap]
    confidence_version: str = "1.0"
