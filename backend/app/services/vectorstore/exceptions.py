class VectorStoreError(Exception):
    """Exception raised for general vector store failures."""
    pass

class CollectionError(VectorStoreError):
    """Exception raised when a vector store collection encounters an error."""
    pass
