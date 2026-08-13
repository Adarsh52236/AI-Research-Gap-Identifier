"""Manual test for Gap Report generation."""
# Run with: PYTHONPATH=. python backend/scripts/manual_gap_report_test.py
import sys
import asyncio
from pathlib import Path
from backend.app.core.fetcher.fetcher_manager import FetcherManager
from backend.app.core.downloader.pdf_downloader import PDFDownloader
from backend.app.core.extractor.extraction_service import ExtractionService
from backend.app.core.gap_analyzer.gap_signal_service import GapSignalService
from backend.app.core.embeddings.indexing_service import EmbeddingIndexingService
from backend.app.core.gap_analyzer.gap_report_service import GapReportService
from backend.app.db.schemas import GapReportRequest

sys.stdout.reconfigure(encoding='utf-8')

async def main():
    manager = FetcherManager()
    downloader = PDFDownloader()
    extractor = ExtractionService()
    gap_signals = GapSignalService()
    indexer = EmbeddingIndexingService()
    report_service = GapReportService()
    
    print("1. Searching...")
    results = await manager.search_all(query="LLM token limit context window constraints", limit=3, sources=["arxiv"])
    target = next((p for p in results if p.pdf_url), None)
    if not target: return
        
    pid = FetcherManager.build_stable_paper_id(target.doi, target.title, target.year, target.source)
    print(f"\n2. Downloading {target.title}...")
    dl = await downloader.download_pdf(target.pdf_url, pid, target.source, target.title, target.year)
    
    print("\n3. Extracting sections...")
    ext = extractor.extract_and_process(Path(dl.local_path), pid, True)
    
    print("\n4. Mining Signals...")
    gap_signals.process_mining_request([pid], None, 20, None, True)
    
    print("\n5. Indexing Embeddings...")
    indexer.index_from_sections_json(Path(ext.sections_path), pid, None, None, None, ["ABSTRACT", "CONCLUSION"], True, True)
    
    print("\n6. Generating Groq Gap Report (takes 5-20s)...")
    req = GapReportRequest(
        paper_ids=[pid],
        query="Context length limitations",
        use_vector_search=True
    )
    
    resp = await report_service.generate_report(req)
    
    print("\n--- GAP REPORT SUCCESS ---")
    print(f"Saved to: {resp.report_md_path}")
    print(f"Total Gaps: {len(resp.report.gaps)}\n")
    
    for i, g in enumerate(resp.report.gaps[:3], 1):
        print(f"{i}. {g.title} (Conf: {g.confidence})")
        print(f"   Citations: {g.citations}")
        print(f"   Summary: {g.summary}\n")

if __name__ == "__main__":
    asyncio.run(main())
