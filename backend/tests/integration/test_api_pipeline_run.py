"""Integration tests for the batch pipeline runner."""
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.config import settings
from backend.app.db.schemas import PaperMetadata, IndexEmbeddingsResponse, GapReportResponse, GapReport
from backend.app.core.fetcher.fetcher_manager import FetcherManager
from backend.app.core.downloader.pdf_downloader import PDFDownloader
from backend.app.core.extractor.extraction_service import ExtractionService
from backend.app.core.gap_analyzer.gap_signal_service import GapSignalService
from backend.app.core.embeddings.indexing_service import EmbeddingIndexingService
from backend.app.core.gap_analyzer.gap_report_service import GapReportService
from backend.app.core.gap_analyzer.groq_client import GroqLLMClient
from backend.app.core.deps import get_current_user
from backend.app.db.models import User
from pathlib import Path

def mock_get_current_user():
    return User(id=1, username="test", email="test@test.com")

app.dependency_overrides[get_current_user] = mock_get_current_user

client = TestClient(app)

def test_api_pipeline_run(tmp_path, monkeypatch):
    storage_dir = tmp_path / "storage"
    runs_dir = storage_dir / "runs"
    processed_dir = storage_dir / "processed"
    downloads_dir = storage_dir / "downloads"
    
    storage_dir.mkdir(parents=True, exist_ok=True)
    
    monkeypatch.setattr(settings, "STORAGE_DIR", str(storage_dir))
    monkeypatch.setattr(settings, "RUNS_DIR", str(runs_dir))
    monkeypatch.setattr(settings, "PROCESSED_DIR", str(processed_dir))
    monkeypatch.setattr(settings, "DOWNLOADS_DIR", str(downloads_dir))
    
    # Mocks
    async def mock_search_all(*args, **kwargs):
        return [
            PaperMetadata(paper_id="paper1", title="Paper 1", source="arxiv", pdf_url="http://arxiv/1"),
            PaperMetadata(paper_id="paper2", title="Paper 2", source="semantic_scholar", pdf_url="http://ss/2")
        ]
    monkeypatch.setattr(FetcherManager, "search_all", mock_search_all)
    
    async def mock_download_pdf(self, pdf_url, paper_id, source, title, year=None, *args, **kwargs):
        year_str = str(year) if year else "unknown"
        pdf_path = Path(settings.DOWNLOADS_DIR) / str(source) / year_str / f"{paper_id}.pdf"
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        pdf_path.touch()
        from backend.app.db.schemas import DownloadPaperResponse
        return DownloadPaperResponse(
            paper_id=paper_id,
            source=source,
            local_path=str(pdf_path),
            storage_path=None,
            status="success",
            sha256="mock_hash",
            size_bytes=1000
        )
    monkeypatch.setattr(PDFDownloader, "download_pdf", mock_download_pdf)
    
    def mock_extract_and_process(self, local_pdf_path, paper_id, *args, **kwargs):
        from backend.app.db.schemas import ExtractPaperResponse
        raw_text = Path(settings.PROCESSED_DIR) / paper_id / "raw.txt"
        raw_text.parent.mkdir(parents=True, exist_ok=True)
        raw_text.touch()
        return ExtractPaperResponse(
            status="success",
            paper_id=paper_id,
            local_pdf_path=str(local_pdf_path),
            raw_text_path=str(raw_text),
            sections_path=None,
            storage_path=None,
            extracted_chars=1000,
            sections_found=[]
        )
    monkeypatch.setattr(ExtractionService, "extract_and_process", mock_extract_and_process)
    
    def mock_process_mining_request(*args, **kwargs):
        pass
    monkeypatch.setattr(GapSignalService, "process_mining_request", mock_process_mining_request)
    
    def mock_index_paper_ids(*args, **kwargs):
        return IndexEmbeddingsResponse(status="indexed", indexed_count=2, skipped_count=0, collection="test")
    monkeypatch.setattr(EmbeddingIndexingService, "index_paper_ids", mock_index_paper_ids)
    
    async def mock_generate_report(*args, **kwargs):
        rep = GapReport(status="success", created_at="now", model="test", paper_ids=["paper1", "paper2"], gaps=[])
        return GapReportResponse(status="success", report=rep, report_md_path=str(storage_dir / "report.md"))
    monkeypatch.setattr(GapReportService, "generate_report", mock_generate_report)
    
    async def mock_parse_prompt(*args, **kwargs):
        return {"extracted_url": None, "optimized_query": "KV cache optimization"}
    monkeypatch.setattr(GroqLLMClient, "parse_user_prompt_json", mock_parse_prompt)
    
    # We will write the report file since the report generation claims it does
    with open(storage_dir / "report.md", "w") as f:
        f.write("# Dummy Report")
        
    response = client.post("/api/v1/analysis/pipeline-run/", json={
        "query": "KV cache optimization",
        "user_document_text": "This is a mock user document that is long enough to bypass the validation check so the pipeline can proceed without exceptions.",
        "limit": 2,
        "steps": ["search", "download", "extract", "mine", "index", "report"]
    })
    
    assert response.status_code == 200
    data = response.json()
    print("PIPELINE ERRORS:", data.get("errors", []))
    assert data["status"] == "completed"
    assert data["papers_found"] == 2
    assert data["papers_downloaded"] == 2
    assert data["papers_extracted"] == 2
    assert data["papers_mined"] == 2
    assert data["papers_indexed"] == 2
    assert data["report_path"] is not None
    
    run_id = data["run_id"]
    
    # Check GET
    get_res = client.get(f"/api/v1/analysis/pipeline-run/{run_id}")
    assert get_res.status_code == 200
    assert get_res.json()["status"] == "completed"
    
    # Check GET report
    rep_res = client.get(f"/api/v1/analysis/pipeline-run/{run_id}/report")
    assert rep_res.status_code == 200
    assert "# Dummy Report" in rep_res.json()["content"]
