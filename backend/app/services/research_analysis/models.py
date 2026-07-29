from dataclasses import dataclass
from typing import List
from datetime import datetime
from app.services.topic_modeling.models import TopicModelResult
from app.services.gap_detection.models import GapDetectionResult
from app.services.llm_reasoning.models import ResearchInsight

@dataclass
class ResearchAnalysisResult:
    """Represents the complete output of an end-to-end research analysis run."""
    query: str
    papers_indexed: int
    topics: TopicModelResult
    gaps: GapDetectionResult
    insights: List[ResearchInsight]
    started_at: datetime
    completed_at: datetime
    duration_seconds: float
