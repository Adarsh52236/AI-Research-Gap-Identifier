"""Embedding Generator."""
import math
import torch
torch.set_num_threads(1)
from backend.app.config import settings
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)

class EmbeddingGenerator:
    _instance = None
    
    def __init__(self):
        self.model = None
        
    def _load_model(self):
        if self.model is None:
            logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL_NAME}")
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME, device=settings.EMBEDDING_DEVICE)
            
    def _normalize(self, vector: list[float]) -> list[float]:
        """Pure python L2 normalization."""
        norm = math.sqrt(sum(x * x for x in vector))
        if norm == 0:
            return vector
        return [x / norm for x in vector]

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
            
        self._load_model()
        # encode returns a list of tensors or numpy arrays depending on kwargs
        # converting directly to python lists for compatibility
        raw_embeddings = self.model.encode(texts, convert_to_numpy=True).tolist()
        
        # normalize
        return [self._normalize(v) for v in raw_embeddings]

def get_embedding_generator() -> EmbeddingGenerator:
    if EmbeddingGenerator._instance is None:
        EmbeddingGenerator._instance = EmbeddingGenerator()
    return EmbeddingGenerator._instance
