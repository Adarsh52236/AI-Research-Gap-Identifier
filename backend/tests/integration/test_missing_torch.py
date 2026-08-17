import pytest
import json
from unittest.mock import patch
from backend.app.db.schemas import PipelineRunRequest, GapReportRequest
from backend.app.core.pipeline.pipeline_runner import PipelineRunner
from backend.app.core.gap_analyzer.gap_report_service import GapReportService
from backend.app.core.embeddings.similarity_search import SimilaritySearchService
from backend.app.db.schemas import EvidenceItem

@pytest.mark.asyncio
async def test_pipeline_continues_without_torch(monkeypatch):
    # Mock embedding generator to raise RuntimeError to simulate missing torch
    def mock_embed_texts(*args, **kwargs):
        raise RuntimeError("PyTorch (torch) is required for sentence-transformers embeddings.")
        
    monkeypatch.setattr("backend.app.core.embeddings.embedding_generator.EmbeddingGenerator.embed_texts", mock_embed_texts)
    
    # We also mock SimilaritySearchService search to raise error, 
    # which simulates what happens when embed_texts fails inside search
    def mock_search(*args, **kwargs):
        raise RuntimeError("PyTorch (torch) is required for sentence-transformers embeddings.")
        
    monkeypatch.setattr("backend.app.core.embeddings.similarity_search.SimilaritySearchService.search", mock_search)
    
    # We mock out LLM to avoid real API calls
    async def mock_llm_json(*args, **kwargs):
        return json.dumps({
            "gaps": [
                {
                    "gap_id": "gap_1",
                    "title": "Mock Gap",
                    "summary": "Mock summary",
                    "why_it_is_a_gap": "Because",
                    "confidence": 0.9,
                    "citations": ["sig_mock1"],
                    "proposed_research_questions": ["Q1"],
                    "suggested_methodology": ["M1"],
                    "suggested_evaluation": ["E1"],
                    "risks_and_limitations": ["R1"]
                }
            ],
            "notes": "Mock notes",
            "user_document_critique": "Critique"
        })
        
    monkeypatch.setattr("backend.app.core.gap_analyzer.groq_client.GroqLLMClient.generate_gap_report_json", mock_llm_json)
    monkeypatch.setattr("backend.app.core.gap_analyzer.groq_client.GroqLLMClient.parse_user_prompt_json", lambda *a, **kw: {"optimized_query": "test"})
    
    runner = PipelineRunner()
    
    # We only test the indexing and report steps, but we need dummy paper IDs
    # So we'll skip download/extract/mine and just do index + report on a dummy paper
    # However, pipeline runner expects valid_paper_ids to be populated by search/download.
    # So let's test GapReportService directly for the report part:
    
    report_service = GapReportService()
    
    # We need to mock safe_resolve_under to return a dummy path that exists, and open() to return mock gap signals
    class MockPath:
        def __init__(self, path="mock_path"):
            self.path = str(path)
        def exists(self): return True
        def __str__(self): return self.path
        def as_posix(self): return self.path
        def __truediv__(self, other): return MockPath(self.path + "/" + str(other))
        
    monkeypatch.setattr("backend.app.core.gap_analyzer.gap_report_service.safe_resolve_under", lambda *a, **kw: MockPath("gap_signals.json"))
    
    import builtins
    original_open = builtins.open
    def mock_open(path, *args, **kwargs):
        if "gap_signals.json" in str(path):
            from io import StringIO
            return StringIO(json.dumps([{"signal_id": "mock1", "sentence": "Test sentence", "score": 0.9}]))
        return original_open(path, *args, **kwargs)
        
    monkeypatch.setattr("builtins.open", mock_open)
    
    req = GapReportRequest(
        paper_ids=["dummy_paper"],
        query="test query",
        use_vector_search=True,
        save_report=False
    )
    
    res = await report_service.generate_report(req)
    
    assert res.status == "ok"
    assert len(res.report.gaps) > 0
    # verify use_vector_search was set to False internally due to the try/except
    assert req.use_vector_search == False
