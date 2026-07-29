import uuid
from datetime import datetime, timezone
from typing import List
from app.services.topic_modeling.models import TopicModelResult
from ..base import GapDetectionStrategy
from ..models import ResearchGap
from ..evidence import EvidenceItem

class TemporalGapStrategy(GapDetectionStrategy):
    """Detects publication inactivity followed by recent growth."""
    
    @property
    def name(self) -> str:
        return "TemporalGapStrategy"
        
    def detect(self, topic_result: TopicModelResult) -> List[ResearchGap]:
        # Relies on temporal metadata which is currently optional/missing.
        return []
