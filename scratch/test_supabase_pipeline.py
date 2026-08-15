import asyncio
from backend.app.db.schemas import PipelineRunRequest
from backend.app.core.pipeline.pipeline_runner import PipelineRunner
from backend.app.config import settings

async def main():
    print(f"VECTOR_BACKEND: {settings.VECTOR_BACKEND}")
    print(f"ARTIFACT_BACKEND: {settings.ARTIFACT_BACKEND}")
    print("Running pipeline...")
    runner = PipelineRunner()
    request = PipelineRunRequest(
        query="Self supervised learning in computer vision",
        limit=1,
        user_document_text="This is a mock research paper for testing. It has to be longer than 50 characters to pass the validation check in the pipeline runner.",
        steps=["search", "download", "extract", "mine", "index", "report"],
        force_report=True
    )
    status = await runner.run(request)
    print(f"Pipeline finished with status: {status.status}")
    print(f"Papers downloaded: {status.papers_downloaded}")
    print(f"Papers extracted: {status.papers_extracted}")
    print(f"Papers mined: {status.papers_mined}")
    print(f"Papers indexed: {status.papers_indexed}")
    print(f"Report path: {status.report_path}")
    print(f"Errors: {status.errors}")

if __name__ == "__main__":
    asyncio.run(main())
