import pytest
import asyncio
from backend.app.db.schemas import PipelineRunRequest
from backend.app.core.pipeline.pipeline_runner import PipelineRunner
from backend.app.config import settings

@pytest.mark.asyncio
async def test_index_timeout(monkeypatch):
    # Set a tiny timeout for the index step
    monkeypatch.setattr(settings, "INDEX_STEP_MAX_SECONDS", 1)
    monkeypatch.setattr(settings, "DB_ENABLED", False)
    
    runner = PipelineRunner()
    
    # Mock indexer to sleep for 3 seconds
    original_index = runner.indexer.index_paper_ids
    def mock_index(*args, **kwargs):
        import time
        time.sleep(3) # blocking sleep, or asyncio.sleep doesn't matter because it runs in threadpool
        return original_index(*args, **kwargs)
    
    monkeypatch.setattr(runner.indexer, "index_paper_ids", mock_index)
    
    request = PipelineRunRequest(
        query="test query for timeout",
        steps=["search", "index"],
        limit=1
    )
    
    # Run pipeline
    status = await runner.run(request)
    
    assert status.status == "completed" or status.status == "failed"
    # the index step should have failed
    assert status.step_statuses.get("index") == "failed"
    # verify error message
    assert any("timed out" in err for err in status.errors)
