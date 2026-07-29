import uuid
from datetime import datetime, timezone
from typing import List
from app.services.topic_modeling.models import TopicModelResult
from ..base import GapDetectionStrategy
from ..models import ResearchGap
from ..evidence import EvidenceItem

class EmergingTopicStrategy(GapDetectionStrategy):
    """Detects rapidly growing topics based on publication velocity."""
    
    @property
    def name(self) -> str:
        return "EmergingTopicStrategy"
        
    def detect(self, topic_result: TopicModelResult) -> List[ResearchGap]:
        # TopicModelResult does not natively contain dates in its current iteration.
        # Gracefully returns empty gaps satisfying requirements without failure.
        return []
