import uuid
from datetime import datetime, timezone
from typing import List
from app.core.config import settings
from app.services.topic_modeling.models import TopicModelResult
from ..base import GapDetectionStrategy
from ..models import ResearchGap
from ..evidence import EvidenceItem

class OutlierStrategy(GapDetectionStrategy):
    """Analyzes BERTopic outlier ratio to determine fragmented domains."""
    
    @property
    def name(self) -> str:
        return "OutlierStrategy"
        
    def detect(self, topic_result: TopicModelResult) -> List[ResearchGap]:
        threshold = settings.gap_detection_config.get("outlier_ratio_threshold", 0.5)
        
        if not topic_result.assignments:
            return []
            
        outlier_count = topic_result.outlier_count
        total_docs = len(topic_result.assignments)
        
        if total_docs == 0:
            return []
            
        ratio = outlier_count / total_docs
        
        if ratio >= threshold:
            evidence = [
                EvidenceItem(
                    category="Fragmentation",
                    message=f"Outlier ratio is {ratio:.2%} ({outlier_count}/{total_docs}), exceeding threshold of {threshold:.2%}",
                    numeric_value=ratio
                )
            ]
            gap = ResearchGap(
                id=str(uuid.uuid4()),
                title="Highly Fragmented Research Domain",
                description="A large percentage of documents could not be clustered, suggesting disjointed or highly novel research without established paradigms.",
                confidence=ratio, # Higher ratio = higher confidence
                strategy=self.name,
                supporting_topics=[-1],
                evidence=evidence,
                created_at=datetime.now(timezone.utc)
            )
            return [gap]
            
        return []
