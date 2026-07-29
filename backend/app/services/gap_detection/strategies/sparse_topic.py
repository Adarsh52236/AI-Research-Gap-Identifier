import uuid
from datetime import datetime, timezone
from typing import List
from app.core.config import settings
from app.services.topic_modeling.models import TopicModelResult
from ..base import GapDetectionStrategy
from ..models import ResearchGap
from ..evidence import EvidenceItem

class SparseTopicStrategy(GapDetectionStrategy):
    """Detects unusually small topics which may indicate emerging, under-researched areas."""
    
    @property
    def name(self) -> str:
        return "SparseTopicStrategy"
        
    def detect(self, topic_result: TopicModelResult) -> List[ResearchGap]:
        threshold = settings.gap_detection_config.get("sparse_topic_threshold", 10)
        gaps = []
        
        for topic in topic_result.topics:
            if topic.id != -1 and 0 < topic.document_count <= threshold:
                evidence = [
                    EvidenceItem(
                        category="Volume",
                        message=f"Topic '{topic.name}' only contains {topic.document_count} documents (threshold: {threshold}).",
                        numeric_value=float(topic.document_count)
                    )
                ]
                gap = ResearchGap(
                    id=str(uuid.uuid4()),
                    title=f"Sparse Topic: {topic.name}",
                    description="Topic has unusually low publication volume, indicating a potential niche or nascent gap.",
                    confidence=0.5, # Base confidence
                    strategy=self.name,
                    supporting_topics=[topic.id],
                    evidence=evidence,
                    created_at=datetime.now(timezone.utc)
                )
                gaps.append(gap)
                
        return gaps
