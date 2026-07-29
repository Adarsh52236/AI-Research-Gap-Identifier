class TopicModelError(Exception):
    """Exception raised for general topic modeling failures."""
    pass

class ModelTrainingError(TopicModelError):
    """Exception raised when topic model training fails."""
    pass
