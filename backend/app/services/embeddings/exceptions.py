class EmbeddingError(Exception):
    """Exception raised for general embedding failures."""
    pass

class ModelLoadError(EmbeddingError):
    """Exception raised when an embedding model fails to load."""
    pass
