import time
from datetime import datetime, timezone
from typing import List, Optional

from app.core.config import settings
from .base import EmbeddingProvider
from .models import EmbeddingResult
from .exceptions import ModelLoadError, EmbeddingError
from app.core.logging import logger

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

class SentenceTransformerProvider(EmbeddingProvider):
    """Embedding provider using the sentence-transformers library."""
    
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.embedding_model_name
        self.provider_name = "SentenceTransformer"
        self._model = None

    def _get_model(self):
        """Lazily loads and caches the SentenceTransformer model."""
        if self._model is None:
            if SentenceTransformer is None:
                raise ModelLoadError("sentence-transformers library is not installed.")
                
            logger.info(f"Loading SentenceTransformer model: {self.model_name}")
            try:
                self._model = SentenceTransformer(self.model_name)
                logger.info(f"Model {self.model_name} initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to load model {self.model_name}: {e}")
                raise ModelLoadError(f"Failed to load model {self.model_name}: {e}") from e
        return self._model

    def embed(self, text: str) -> EmbeddingResult:
        if not text or not text.strip():
            raise EmbeddingError("Input text cannot be empty or whitespace-only.")
            
        logger.info("Generating embedding for a single text.")
        start_time = time.perf_counter()
        
        try:
            model = self._get_model()
            # encode() directly returns numpy arrays for sentence-transformers
            embedding = model.encode(text)
            vector = embedding.tolist()
            
            duration = time.perf_counter() - start_time
            logger.info(f"Embedding generated in {duration:.4f} seconds.")
            
            return EmbeddingResult(
                vector=vector,
                dimensions=len(vector),
                model_name=self.model_name,
                provider_name=self.provider_name,
                created_at=datetime.now(timezone.utc)
            )
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise EmbeddingError(f"Embedding generation failed: {e}") from e

    def embed_batch(self, texts: List[str]) -> List[EmbeddingResult]:
        if not texts:
            return []
            
        valid_texts = []
        for i, text in enumerate(texts):
            if not text or not text.strip():
                raise EmbeddingError(f"Input text at index {i} cannot be empty or whitespace-only.")
            valid_texts.append(text)
            
        batch_size = len(valid_texts)
        logger.info(f"Generating embeddings for a batch of {batch_size} texts.")
        start_time = time.perf_counter()
        
        try:
            model = self._get_model()
            # Perform a single batch encode
            embeddings = model.encode(valid_texts)
            
            results = []
            now = datetime.now(timezone.utc)
            for emb in embeddings:
                vector = emb.tolist()
                results.append(EmbeddingResult(
                    vector=vector,
                    dimensions=len(vector),
                    model_name=self.model_name,
                    provider_name=self.provider_name,
                    created_at=now
                ))
                
            duration = time.perf_counter() - start_time
            logger.info(f"Batch embedding generated in {duration:.4f} seconds.")
            
            return results
        except Exception as e:
            logger.error(f"Batch embedding generation failed: {e}")
            raise EmbeddingError(f"Batch embedding generation failed: {e}") from e
