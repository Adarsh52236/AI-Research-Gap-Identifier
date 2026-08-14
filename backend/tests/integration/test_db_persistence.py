"""Tests for SQLAlchemy DB Persistence."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.db.session import Base
from backend.app.db.models import Paper, PipelineRunRow, GapSignalRow
from backend.app.db.schemas import PaperMetadata, PipelineRunStatus, GapSignal
from backend.app.db import crud

@pytest.fixture
def db_session(tmp_path):
    # Use SQLite in-memory for fast testing
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_upsert_paper(db_session):
    p_meta = PaperMetadata(
        paper_id="test-123",
        title="Test Paper",
        source="arxiv",
        year=2024
    )
    paper = crud.upsert_paper(db_session, p_meta)
    
    assert paper.paper_id == "test-123"
    assert paper.title == "Test Paper"
    
    # Upsert with new title
    p_meta.title = "Updated Title"
    paper2 = crud.upsert_paper(db_session, p_meta)
    assert paper2.title == "Updated Title"
    
    # Check total rows
    assert db_session.query(Paper).count() == 1

def test_create_or_update_run(db_session):
    status = PipelineRunStatus(
        run_id="run-1",
        status="running",
        query="test",
        steps=["search"],
        started_at="2026-08-14T00:00:00Z"
    )
    row = crud.create_or_update_run(db_session, status)
    
    assert row.run_id == "run-1"
    assert row.status == "running"
    
    status.status = "completed"
    row2 = crud.create_or_update_run(db_session, status)
    assert row2.status == "completed"
    
    assert db_session.query(PipelineRunRow).count() == 1

def test_save_gap_signals(db_session):
    # Create paper first to satisfy foreign key
    crud.upsert_paper(db_session, PaperMetadata(paper_id="paper-1", title="A", source="b"))
    
    sig = GapSignal(
        signal_id="sig-1",
        paper_id="paper-1",
        section="INTRODUCTION",
        sentence="We need better evaluation.",
        pattern="evaluation_gap",
        score=0.9,
        evidence={"text": "We need better evaluation."}
    )
    
    crud.save_gap_signals(db_session, [sig])
    
    row = db_session.query(GapSignalRow).first()
    assert row is not None
    assert row.signal_id == "sig-1"
    assert row.paper_id == "paper-1"
    assert row.score == 0.9
    assert row.quality_score == 1.0
