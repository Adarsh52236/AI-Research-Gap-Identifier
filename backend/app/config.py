"""All env/config settings."""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

class Settings(BaseSettings):
    STORAGE_DIR: str = "storage"
    DOWNLOADS_DIR: str = "storage/downloads"
    PROCESSED_DIR: str = "storage/processed"
    RUNS_DIR: str = "storage/runs"
    CHROMA_DB_PATH: str = "storage/chromadb"
    CHROMA_COLLECTION_NAME: str = "papers_sections_v2"
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_MAX_CHARS: int = 12000
    INDEX_SECTIONS_DEFAULT: str = "ABSTRACT,INTRODUCTION,RELATED WORK,METHODS,EXPERIMENTS,RESULTS,DISCUSSION,CONCLUSION,FUTURE WORK,LIMITATIONS"
    EMBEDDING_DEVICE: str = "cpu"
    MAX_PDF_SIZE_MB: int = 50
    HTTP_TIMEOUT_SECONDS: int = 30
    
    # Phase 5
    REPORTS_DIR: str = "storage/reports"
    GROQ_API_KEY: str | None = None
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_TEMPERATURE: float = 0.2
    GROQ_MAX_TOKENS: int = 1200
    GROQ_TIMEOUT_SECONDS: int = 60
    EVIDENCE_MAX_CHARS: int = 900
    REPORT_TOP_K_GAPS: int = 7
    
    # Database
    DATABASE_URL: str | None = None
    DB_ENABLED: bool = True
    
    # Deployment & Security
    ALLOWED_ORIGINS: str = "http://localhost:5173"
    ALLOW_CREDENTIALS: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Rate Limits
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_SEARCH: str = "30/minute"
    RATE_LIMIT_DOWNLOAD: str = "10/minute"
    RATE_LIMIT_EXTRACT: str = "10/minute"
    RATE_LIMIT_PIPELINE: str = "3/minute"
    RATE_LIMIT_REPORT: str = "6/minute"

settings = Settings()
