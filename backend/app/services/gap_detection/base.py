from abc import ABC, abstractmethod
from typing import List
from app.services.topic_modeling.models import TopicModelResult
from .models import ResearchGap

class GapDetectionStrategy(ABC):
    """Abstract interface for a research gap detection strategy."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the unique name of the strategy."""
        pass
        
    @abstractmethod
    def detect(self, topic_result: TopicModelResult) -> List[ResearchGap]:
        """Analyzes a topic model result and returns a list of detected research gaps."""
        pass
