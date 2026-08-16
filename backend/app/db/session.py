import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.app.config import settings

# Determine DATABASE_URL
database_url = settings.DATABASE_URL
if database_url:
    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    elif database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)

if not database_url:
    # Fallback to local SQLite file
    db_path = Path(settings.STORAGE_DIR) / "local.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    database_url = f"sqlite:///{db_path}"

# For SQLite, we need check_same_thread=False
connect_args = {}
if database_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

if settings.DB_ENABLED:
    engine = create_engine(database_url, connect_args=connect_args)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
else:
    # Stub it out if DB is disabled entirely
    engine = None
    SessionLocal = None
    Base = declarative_base()

def get_db():
    if not settings.DB_ENABLED or SessionLocal is None:
        yield None
        return
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
