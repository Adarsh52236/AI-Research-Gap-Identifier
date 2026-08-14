import json
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from backend.app.db.session import Base

class Paper(Base):
    __tablename__ = "papers"
    
    paper_id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    abstract = Column(Text, nullable=True)
    authors_json = Column(Text, nullable=True)  # serialized JSON
    year = Column(Integer, nullable=True)
    source = Column(String, nullable=False)
    url = Column(String, nullable=True)
    pdf_url = Column(String, nullable=True)
    doi = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    download_artifact = relationship("DownloadArtifact", back_populates="paper", uselist=False)
    extraction_artifact = relationship("ExtractionArtifact", back_populates="paper", uselist=False)
    gap_signals = relationship("GapSignalRow", back_populates="paper")

class DownloadArtifact(Base):
    __tablename__ = "download_artifacts"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    paper_id = Column(String, ForeignKey("papers.paper_id"), unique=True, index=True)
    local_path = Column(String, nullable=False)
    sha256 = Column(String, nullable=True)
    size_bytes = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    paper = relationship("Paper", back_populates="download_artifact")

class ExtractionArtifact(Base):
    __tablename__ = "extraction_artifacts"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    paper_id = Column(String, ForeignKey("papers.paper_id"), unique=True, index=True)
    raw_text_path = Column(String, nullable=False)
    sections_path = Column(String, nullable=True)
    extracted_chars = Column(Integer, nullable=False)
    sections_found_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    paper = relationship("Paper", back_populates="extraction_artifact")

class GapSignalRow(Base):
    __tablename__ = "gap_signals"
    
    signal_id = Column(String, primary_key=True, index=True)
    paper_id = Column(String, ForeignKey("papers.paper_id"), index=True)
    section = Column(String, nullable=False)
    sentence = Column(Text, nullable=False)
    pattern = Column(String, nullable=False)
    score = Column(Float, nullable=False)
    quality_score = Column(Float, nullable=False, default=1.0)
    is_noise = Column(Boolean, nullable=False, default=False)
    evidence_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    paper = relationship("Paper", back_populates="gap_signals")

class PipelineRunRow(Base):
    __tablename__ = "pipeline_runs"
    
    run_id = Column(String, primary_key=True, index=True)
    status = Column(String, nullable=False)
    current_step = Column(String, nullable=True)
    query = Column(String, nullable=False)
    steps_json = Column(Text, nullable=False)
    papers_found = Column(Integer, default=0)
    papers_downloaded = Column(Integer, default=0)
    papers_extracted = Column(Integer, default=0)
    papers_mined = Column(Integer, default=0)
    papers_indexed = Column(Integer, default=0)
    report_path = Column(String, nullable=True)
    errors_json = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)

class ReportRow(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    run_id = Column(String, ForeignKey("pipeline_runs.run_id"), nullable=True)
    query = Column(String, nullable=True)
    model = Column(String, nullable=False)
    paper_ids_json = Column(Text, nullable=False)
    report_json_path = Column(String, nullable=True)
    report_md_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
