"""Pydantic schemas."""
from pydantic import BaseModel, Field
from typing import List, Optional

class PaperAuthor(BaseModel):
    name: str

class PaperMetadata(BaseModel):
    paper_id: str
    title: str
    abstract: Optional[str] = None
    authors: List[PaperAuthor] = Field(default_factory=list)
    year: Optional[int] = None
    source: str
    url: Optional[str] = None
    pdf_url: Optional[str] = None
    doi: Optional[str] = None

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=3)
    limit: int = Field(20, le=50)
    sources: List[str] = Field(default=["arxiv", "semantic_scholar"])
    year_from: Optional[int] = None
    year_to: Optional[int] = None

class SearchResponse(BaseModel):
    query: str
    count: int
    results: List[PaperMetadata]


class DownloadPaperRequest(BaseModel):
    pdf_url: str
    paper_id: Optional[str] = None
    source: Optional[str] = None
    title: Optional[str] = None
    year: Optional[int] = None

class DownloadPaperResponse(BaseModel):
    status: str
    paper_id: str
    source: Optional[str] = None
    local_path: str
    sha256: str
    size_bytes: int
    content_type: Optional[str] = None


class ExtractPaperRequest(BaseModel):
    local_path: str
    paper_id: Optional[str] = None
    source: Optional[str] = None
    year: Optional[int] = None
    parse_sections: bool = True

class ExtractPaperResponse(BaseModel):
    status: str
    paper_id: str
    local_pdf_path: str
    raw_text_path: str
    sections_path: Optional[str] = None
    extracted_chars: int
    sections_found: list[str]


class GapSignal(BaseModel):
    signal_id: str
    paper_id: str
    source: Optional[str] = None
    year: Optional[int] = None
    section: str
    sentence: str
    pattern: str
    score: float
    quality_score: float = 1.0
    is_noise: bool = False
    evidence: dict

class MineGapSignalsRequest(BaseModel):
    paper_ids: Optional[list[str]] = None
    processed_sections_paths: Optional[list[str]] = None
    top_k: int = 30
    include_sections: Optional[list[str]] = None
    save: bool = True

class MineGapSignalsResponse(BaseModel):
    status: str
    count: int
    results_path: Optional[str] = None
    signals: list[GapSignal]


class IndexEmbeddingsRequest(BaseModel):
    paper_ids: Optional[list[str]] = None
    processed_sections_paths: Optional[list[str]] = None
    sections: Optional[list[str]] = None
    force_reindex: bool = False
    save_text: bool = True

class IndexEmbeddingsResponse(BaseModel):
    status: str
    indexed_count: int
    skipped_count: int
    collection: str

class SimilaritySearchRequest(BaseModel):
    query_text: str
    top_k: int = 10
    filter_source: Optional[str] = None
    filter_year_from: Optional[int] = None
    filter_year_to: Optional[int] = None
    filter_section: Optional[str] = None

class SimilarityMatch(BaseModel):
    id: str
    paper_id: str
    section: str
    score: float
    distance: float
    preview: Optional[str] = None
    metadata: dict

class SimilaritySearchResponse(BaseModel):
    status: str
    count: int
    results: list[SimilarityMatch]


class EvidenceItem(BaseModel):
    evidence_id: str
    paper_id: str
    source_type: str
    section: Optional[str] = None
    score: Optional[float] = None
    text: str
    metadata: dict

class GapCandidate(BaseModel):
    gap_id: str
    title: str
    summary: str
    why_it_is_a_gap: str
    proposed_research_questions: list[str]
    suggested_methodology: list[str]
    suggested_evaluation: list[str]
    risks_and_limitations: list[str]
    citations: list[str]
    confidence: float

class GapReport(BaseModel):
    status: str
    query: Optional[str] = None
    created_at: str
    model: str
    paper_ids: list[str]
    user_document_critique: Optional[str] = None
    gaps: list[GapCandidate]
    notes: Optional[str] = None

class GapReportRequest(BaseModel):
    paper_ids: list[str]
    query: Optional[str] = None
    user_document_text: Optional[str] = None
    top_k_signals_per_paper: int = 20
    top_k_sections_from_vector_search: int = 5
    use_vector_search: bool = True
    sections_filter: Optional[list[str]] = None
    save_report: bool = True

class GapReportResponse(BaseModel):
    status: str
    report: GapReport
    report_json_path: Optional[str] = None
    report_md_path: Optional[str] = None

class PipelineRunRequest(BaseModel):
    run_id: Optional[str] = None
    query: str
    user_document_text: Optional[str] = None
    limit: int = 5
    sources: list[str] = ["arxiv", "semantic_scholar"]
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    steps: list[str] = ["search", "download", "extract", "mine", "index", "report"]
    force_reindex: bool = False
    force_report: bool = False
    top_k_papers_for_report: int = 25
    report_query: Optional[str] = None
    save: bool = True

class PipelineRunStatus(BaseModel):
    run_id: str
    user_id: Optional[int] = None
    status: str
    current_step: Optional[str] = None
    started_at: str
    finished_at: Optional[str] = None
    query: str
    steps: list[str]
    papers_found: int = 0
    papers_downloaded: int = 0
    papers_extracted: int = 0
    papers_mined: int = 0
    papers_indexed: int = 0
    report_path: Optional[str] = None
    errors: list[str] = Field(default_factory=list)

class ReviewAnnotateRequest(BaseModel):
    prompt: Optional[str] = None
    compare_papers_limit: int = 0
    annotations_target: int = 12
    style_guide: Optional[str] = None
    strict_no_hallucination: bool = True

class ReviewAnnotateResponse(BaseModel):
    status: str
    review_run_id: str
    input_pdf_path: str
    annotated_pdf_path: str
    issues_count: int
    dropped_count: int
    notes: Optional[str] = None

class ReviewEvidence(BaseModel):
    evidence_id: str
    page_hint: Optional[int] = None
    anchor_phrase: str
    quote: str
    section: Optional[str] = None

class ReviewIssue(BaseModel):
    issue_id: str
    severity: str
    issue: str
    solution: str
    evidence: ReviewEvidence
    issue_type: str

class ReviewLLMOutput(BaseModel):
    issues: list[ReviewIssue]
    overall_issues: list[str]
    overall_solutions: list[str]

