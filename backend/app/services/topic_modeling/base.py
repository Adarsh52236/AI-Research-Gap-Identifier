from abc import ABC, abstractmethod
from typing import List
from .models import TopicModelResult, TopicModelMetadata

class TopicModelProvider(ABC):
    """Abstract interface for all topic modeling providers."""
    
    @abstractmethod
    def fit(self, documents: List[str]) -> TopicModelResult:
        """Trains the topic model on the provided documents and returns the extracted topics and assignments."""
        pass
        
    @abstractmethod
    def transform(self, documents: List[str]) -> TopicModelResult:
        """Assigns the provided documents to topics using the currently trained model."""
        pass
        
    @abstractmethod
    def save_model(self, path: str) -> None:
        """Saves the trained model to the specified path."""
        pass
        
    @abstractmethod
    def load_model(self, path: str) -> None:
        """Loads a trained model from the specified path."""
        pass

    @abstractmethod
    def get_model_metadata(self) -> TopicModelMetadata:
        """Returns the metadata of the currently loaded or trained model."""
        pass
