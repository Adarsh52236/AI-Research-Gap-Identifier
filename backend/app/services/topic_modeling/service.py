import time
from typing import List, Optional
from app.core.logging import logger

from .base import TopicModelProvider
from .models import TopicModelResult
from .exceptions import TopicModelError
from .model_registry import TopicModelRegistry

class TopicModelingService:
    """Orchestrates topic modeling operations via dependency injection."""
    
    def __init__(self, provider: TopicModelProvider, registry: Optional[TopicModelRegistry] = None):
        """
        Initializes the service with a specific topic modeling provider and an optional registry.
        """
        self.provider = provider
        self.registry = registry
        logger.info("TopicModelingService initialized.")

    def save_model(self, path: str, version: Optional[str] = None) -> None:
        """Saves the underlying trained model to disk and registers its metadata."""
        logger.info(f"TopicModelingService: saving model to {path}")
        self.provider.save_model(path)
        
        if self.registry:
            try:
                metadata = self.provider.get_model_metadata()
                # Assign an automatic timestamp-based version if none provided
                metadata.version = version or f"v{int(time.time())}"
                self.registry.register_model(metadata)
            except Exception as e:
                logger.error(f"Failed to register model metadata during save: {e}")

    def load_model(self, path: str) -> None:
        """Loads a model from disk into the provider."""
        logger.info(f"TopicModelingService: loading model from {path}")
        self.provider.load_model(path)
        
    def train(self, documents: List[str]) -> TopicModelResult:
        """
        Trains the topic model on a corpus of documents.
        """
        logger.info(f"Topic modeling training started for {len(documents)} documents.")
        try:
            result = self.provider.fit(documents)
            logger.info(f"Topic modeling training completed in {result.training_duration:.4f}s.")
            logger.info(f"Discovered {len(result.topics)} topics with {result.outlier_count} outliers.")
            return result
        except Exception as e:
            logger.error(f"Topic modeling training failed: {e}")
            raise TopicModelError(f"Failed to train topic model: {e}") from e

    def assign_topics(self, documents: List[str]) -> TopicModelResult:
        """
        Assigns topics to a list of documents using the currently trained model.
        """
        logger.info(f"Topic assignment started for {len(documents)} documents.")
        try:
            result = self.provider.transform(documents)
            logger.info(f"Topic assignment completed successfully in {result.training_duration:.4f}s.")
            return result
        except Exception as e:
            logger.error(f"Topic assignment failed: {e}")
            raise TopicModelError(f"Failed to assign topics: {e}") from e
