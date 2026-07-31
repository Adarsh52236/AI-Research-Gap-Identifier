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
    # LLM Settings
    llm_provider: str = "groq"
    groq_api_key: str | None = None
    groq_model: str = "llama-3.3-70b-versatile"

    # JWT Authentication
    secret_key: str = "supersecret_default_key_change_in_production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

settings = Settings()
