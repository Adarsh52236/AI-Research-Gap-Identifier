"""All env/config settings."""
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
load_dotenv("backend/.env")

class Settings(BaseSettings):
    ALLOWED_ORIGINS: str = "http://localhost:5173"
    ALLOW_CREDENTIALS: bool = False
    STORAGE_DIR: str = "storage"
    DOWNLOADS_DIR: str = "storage/downloads"
    PROCESSED_DIR: str = "storage/processed"
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

settings = Settings()
