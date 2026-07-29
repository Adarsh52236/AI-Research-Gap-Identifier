import os
import json
from typing import List, Optional
from datetime import datetime
from app.core.logging import logger
from .models import TopicModelMetadata

class TopicModelRegistry:
    """Filesystem-based registry for topic modeling metadata."""
    
    def __init__(self, registry_dir: str = "./model_registry"):
        """Initializes the registry and ensures the directory exists."""
        self.registry_dir = registry_dir
        os.makedirs(self.registry_dir, exist_ok=True)
        logger.info(f"Initialized TopicModelRegistry at {self.registry_dir}")

    def _get_metadata_path(self, version: str) -> str:
        return os.path.join(self.registry_dir, f"{version}.json")

    def register_model(self, metadata: TopicModelMetadata) -> None:
        """Registers a newly trained model's metadata."""
        path = self._get_metadata_path(metadata.version)
        try:
            data = metadata.__dict__.copy()
            data["trained_at"] = data["trained_at"].isoformat()
            
            with open(path, "w") as f:
                json.dump(data, f, indent=4)
            logger.info(f"Registered model metadata for version {metadata.version}")
        except Exception as e:
            logger.error(f"Failed to register model metadata: {e}")
            raise

    def list_models(self) -> List[TopicModelMetadata]:
        """Lists all registered models, sorted by trained_at descending."""
        models = []
        for filename in os.listdir(self.registry_dir):
            if filename.endswith(".json"):
                version = filename[:-5]
                try:
                    models.append(self.get_metadata(version))
                except Exception:
                    pass
        return sorted(models, key=lambda x: x.trained_at, reverse=True)

    def get_latest_model(self) -> Optional[TopicModelMetadata]:
        """Resolves the latest registered model."""
        models = self.list_models()
        return models[0] if models else None

    def get_metadata(self, version: str) -> TopicModelMetadata:
        """Retrieves metadata for a specific model version."""
        path = self._get_metadata_path(version)
        if not os.path.exists(path):
            raise FileNotFoundError(f"No metadata found for version {version}")
            
        with open(path, "r") as f:
            data = json.load(f)
            
        data["trained_at"] = datetime.fromisoformat(data["trained_at"])
        return TopicModelMetadata(**data)
