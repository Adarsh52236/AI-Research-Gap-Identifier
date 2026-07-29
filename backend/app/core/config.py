from typing import Dict, Any
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    project_name: str = "AI Research Gap Identifier API"
    version: str = "0.1.0"
    
    embedding_model_name: str = "all-MiniLM-L6-v2"
    
    # Topic Modeling Defaults
    topic_model_config: Dict[str, Any] = {"language": "english"}
    
    # Gap Detection Defaults
    gap_detection_config: Dict[str, Any] = {
        "sparse_topic_threshold": 10,
        "outlier_ratio_threshold": 0.5,
        "strategy_weights": {
            "SparseTopicStrategy": 1.0,
            "EmergingTopicStrategy": 1.2,
            "OutlierStrategy": 0.8,
            "TemporalGapStrategy": 1.5
        }
    }
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

settings = Settings()
