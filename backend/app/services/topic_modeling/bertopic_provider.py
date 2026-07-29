import time
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from app.core.logging import logger
from app.core.config import settings

from .base import TopicModelProvider
from .models import TopicInfo, TopicModelResult, TopicModelMetadata
from .exceptions import TopicModelError, ModelTrainingError

try:
    from bertopic import BERTopic
    import bertopic
    BERTOPIC_VERSION = bertopic.__version__
except ImportError:
    BERTopic = None
    BERTOPIC_VERSION = "unknown"

class BERTopicProvider(TopicModelProvider):
    """Topic modeling provider using the BERTopic library."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, model: Optional['BERTopic'] = None):
        """
        Initializes the BERTopic provider.
        """
        if BERTopic is None:
            raise TopicModelError("bertopic library is not installed.")
            
        self.config = config if config is not None else settings.topic_model_config
        self._current_metadata: Optional[TopicModelMetadata] = None
        
        if model is not None:
            self.model = model
            self.is_fitted = True
            logger.info("Initialized BERTopicProvider with a pre-trained model.")
        else:
            try:
                self.model = BERTopic(**self.config)
                self.is_fitted = False
                logger.info(f"Initialized new BERTopic model with config: {self.config}")
            except Exception as e:
                logger.error(f"Failed to initialize BERTopic model: {e}")
                raise TopicModelError(f"Failed to initialize BERTopic model: {e}") from e

    def get_model_metadata(self) -> TopicModelMetadata:
        if not self._current_metadata:
            raise TopicModelError("No metadata available. Train a model first.")
        return self._current_metadata

    def save_model(self, path: str) -> None:
        if not self.is_fitted:
            raise TopicModelError("Cannot save an untrained model.")
        logger.info(f"Saving BERTopic model to {path}")
        try:
            self.model.save(path, serialization="safetensors", save_ctfidf=True)
            logger.info("Model saved successfully.")
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            raise TopicModelError(f"Failed to save model: {e}") from e

    def load_model(self, path: str) -> None:
        logger.info(f"Loading BERTopic model from {path}")
        try:
            self.model = BERTopic.load(path)
            self.is_fitted = True
            logger.info("Model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise TopicModelError(f"Failed to load model: {e}") from e

    def _extract_topics_info(self) -> List[TopicInfo]:
        """Helper to extract topic representations from the trained BERTopic model."""
        topics_info = []
        try:
            topic_info_df = self.model.get_topic_info()
            for _, row in topic_info_df.iterrows():
                topics_info.append(TopicInfo(
                    id=row["Topic"],
                    name=row["Name"],
                    document_count=row["Count"]
                ))
            return topics_info
        except Exception as e:
            logger.error(f"Failed to extract topic information: {e}")
            raise TopicModelError(f"Failed to extract topic information: {e}") from e

    def fit(self, documents: List[str]) -> TopicModelResult:
        logger.info(f"Fitting BERTopic model on {len(documents)} documents.")
        start_time = time.perf_counter()
        try:
            topics, _ = self.model.fit_transform(documents)
            self.is_fitted = True
            
            topics_info = self._extract_topics_info()
            duration = time.perf_counter() - start_time
            outlier_count = sum(1 for t in topics if t == -1)
            
            umap_params = {}
            if hasattr(self.model, "umap_model") and hasattr(self.model.umap_model, "get_params"):
                try:
                    umap_params = {k: str(v) for k, v in self.model.umap_model.get_params().items()}
                except Exception: pass
                
            hdbscan_params = {}
            if hasattr(self.model, "hdbscan_model") and hasattr(self.model.hdbscan_model, "get_params"):
                try:
                    hdbscan_params = {k: str(v) for k, v in self.model.hdbscan_model.get_params().items()}
                except Exception: pass

            self._current_metadata = TopicModelMetadata(
                model_name="BERTopic",
                trained_at=datetime.now(timezone.utc),
                document_count=len(documents),
                topic_count=len(topics_info),
                version="", # populated by orchestrator
                embedding_model=self.config.get("embedding_model", settings.embedding_model_name),
                bertopic_version=BERTOPIC_VERSION,
                training_dataset_hash="",
                umap_parameters=umap_params,
                hdbscan_parameters=hdbscan_params
            )
            
            logger.info(f"BERTopic model successfully fitted in {duration:.4f}s.")
            logger.info(f"Extracted {len(topics_info)} topics. Found {outlier_count} outliers.")
            
            return TopicModelResult(
                topics=topics_info,
                assignments=topics,
                training_duration=duration,
                outlier_count=outlier_count
            )
        except Exception as e:
            logger.error(f"BERTopic model training failed: {e}")
            raise ModelTrainingError(f"BERTopic model training failed: {e}") from e

    def transform(self, documents: List[str]) -> TopicModelResult:
        if not self.is_fitted:
            raise TopicModelError("Cannot transform documents: the model has not been trained yet.")
            
        logger.info(f"Assigning topics for {len(documents)} documents using BERTopic.")
        start_time = time.perf_counter()
        try:
            topics, _ = self.model.transform(documents)
            topics_info = self._extract_topics_info()
            
            duration = time.perf_counter() - start_time
            outlier_count = sum(1 for t in topics if t == -1)
            
            logger.info(f"BERTopic transformation completed in {duration:.4f}s. Found {outlier_count} outliers.")
            
            return TopicModelResult(
                topics=topics_info,
                assignments=topics,
                training_duration=duration,
                outlier_count=outlier_count
            )
        except Exception as e:
            logger.error(f"BERTopic transformation failed: {e}")
            raise TopicModelError(f"BERTopic transformation failed: {e}") from e
