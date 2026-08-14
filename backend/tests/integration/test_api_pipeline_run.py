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
from pathlib import Path

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
    
    async def mock_download_pdf(self, req, *args, **kwargs):
        pdf_path = Path(settings.DOWNLOADS_DIR) / req.source / f"{req.paper_id}.pdf"
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        pdf_path.touch()
    monkeypatch.setattr(PDFDownloader, "download_pdf", mock_download_pdf)
    
    def mock_extract_and_process(*args, **kwargs):
        pass
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
    
    # We will write the report file since the report generation claims it does
    with open(storage_dir / "report.md", "w") as f:
        f.write("# Dummy Report")
        
    response = client.post("/api/v1/analysis/pipeline-run/", json={
        "query": "KV cache optimization",
        "limit": 2,
        "steps": ["search", "download", "extract", "mine", "index", "report"]
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["papers_found"] == 2
    print("ERRORS:", data["errors"])
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
