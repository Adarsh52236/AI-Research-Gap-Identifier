import json
from datetime import datetime
from sqlalchemy.orm import Session
from backend.app.db.schemas import (
    PaperMetadata, PipelineRunStatus, DownloadPaperResponse, 
    ExtractPaperResponse, GapSignal, GapReportResponse
)
from backend.app.db.models import (
    Paper, DownloadArtifact, ExtractionArtifact, 
    GapSignalRow, PipelineRunRow, ReportRow
)

def upsert_paper(db: Session, paper_meta: PaperMetadata) -> Paper:
    paper = db.query(Paper).filter(Paper.paper_id == paper_meta.paper_id).first()
    if not paper:
        paper = Paper(paper_id=paper_meta.paper_id)
        db.add(paper)
    
    paper.title = paper_meta.title
    paper.abstract = paper_meta.abstract
    paper.authors_json = json.dumps([a.model_dump() for a in paper_meta.authors])
    paper.year = paper_meta.year
    paper.source = paper_meta.source
    paper.url = paper_meta.url
    paper.pdf_url = paper_meta.pdf_url
    paper.doi = paper_meta.doi
    
    db.commit()
    db.refresh(paper)
    return paper

def save_download_artifact(db: Session, dl_res: DownloadPaperResponse) -> DownloadArtifact:
    artifact = db.query(DownloadArtifact).filter(DownloadArtifact.paper_id == dl_res.paper_id).first()
    if not artifact:
        artifact = DownloadArtifact(paper_id=dl_res.paper_id)
        db.add(artifact)
        
    artifact.local_path = dl_res.local_path
    artifact.sha256 = dl_res.sha256
    artifact.size_bytes = dl_res.size_bytes
    
    db.commit()
    db.refresh(artifact)
    return artifact

def save_extraction_artifact(db: Session, ex_res: ExtractPaperResponse) -> ExtractionArtifact:
    artifact = db.query(ExtractionArtifact).filter(ExtractionArtifact.paper_id == ex_res.paper_id).first()
    if not artifact:
        artifact = ExtractionArtifact(paper_id=ex_res.paper_id)
        db.add(artifact)
        
    artifact.raw_text_path = ex_res.raw_text_path
    artifact.sections_path = ex_res.sections_path
    artifact.extracted_chars = ex_res.extracted_chars
    artifact.sections_found_json = json.dumps(ex_res.sections_found)
    
    db.commit()
    db.refresh(artifact)
    return artifact

def save_gap_signals(db: Session, signals: list[GapSignal]):
    if not signals:
        return
        
    for sig in signals:
        row = db.query(GapSignalRow).filter(GapSignalRow.signal_id == sig.signal_id).first()
        if not row:
            row = GapSignalRow(signal_id=sig.signal_id)
            db.add(row)
            
        row.paper_id = sig.paper_id
        row.section = sig.section
        row.sentence = sig.sentence
        row.pattern = sig.pattern
        row.score = sig.score
        row.quality_score = sig.quality_score
        row.is_noise = sig.is_noise
        row.evidence_json = json.dumps(sig.evidence)
        
    db.commit()

def create_or_update_run(db: Session, status: PipelineRunStatus) -> PipelineRunRow:
    row = db.query(PipelineRunRow).filter(PipelineRunRow.run_id == status.run_id).first()
    if not row:
        row = PipelineRunRow(run_id=status.run_id)
        db.add(row)
        
    row.status = status.status
    row.current_step = status.current_step
    row.query = status.query
    row.steps_json = json.dumps(status.steps)
    row.papers_found = status.papers_found
    row.papers_downloaded = status.papers_downloaded
    row.papers_extracted = status.papers_extracted
    row.papers_mined = status.papers_mined
    row.papers_indexed = status.papers_indexed
    row.report_path = status.report_path
    row.errors_json = json.dumps(status.errors)
    
    if status.started_at:
        try:
            row.started_at = datetime.fromisoformat(status.started_at.replace("Z", "+00:00"))
        except:
            pass
    if status.finished_at:
        try:
            row.finished_at = datetime.fromisoformat(status.finished_at.replace("Z", "+00:00"))
        except:
            pass
        
    db.commit()
    db.refresh(row)
    return row

def save_report(db: Session, run_id: str, report_res: GapReportResponse):
    row = ReportRow(
        run_id=run_id,
        query=report_res.report.query,
        model=report_res.report.model,
        paper_ids_json=json.dumps(report_res.report.paper_ids),
        report_json_path=report_res.report_json_path,
        report_md_path=report_res.report_md_path
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
