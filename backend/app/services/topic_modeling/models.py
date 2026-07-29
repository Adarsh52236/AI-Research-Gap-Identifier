from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime

@dataclass
class TopicInfo:
    """Represents metadata about a discovered topic."""
    id: int
    name: str
    document_count: int

@dataclass
class TopicModelMetadata:
    """Contains metadata about the trained topic model itself."""
    model_name: str
    trained_at: datetime
    document_count: int
    topic_count: int
    version: str
    embedding_model: str = ""
    bertopic_version: str = ""
    training_dataset_hash: str = ""
    umap_parameters: Dict[str, Any] = field(default_factory=dict)
    hdbscan_parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TopicModelResult:
    """Represents the results of a topic modeling assignment or training."""
    topics: List[TopicInfo]
    assignments: List[int]
    training_duration: float = 0.0
    outlier_count: int = 0
