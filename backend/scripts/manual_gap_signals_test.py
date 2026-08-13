"""Manual gap signals mining test script."""
# Run with: PYTHONPATH=. python backend/scripts/manual_gap_signals_test.py
import sys
import asyncio
import json
from pathlib import Path
from backend.app.core.fetcher.fetcher_manager import FetcherManager
from backend.app.core.downloader.pdf_downloader import PDFDownloader
from backend.app.core.extractor.extraction_service import ExtractionService
from backend.app.core.gap_analyzer.gap_signal_service import GapSignalService

sys.stdout.reconfigure(encoding='utf-8')

async def main():
    manager = FetcherManager()
    downloader = PDFDownloader()
    extractor = ExtractionService()
    gap_service = GapSignalService()
    
    print("1. Searching ArXiv for a paper...")
    results = await manager.search_all(query="LLM future work limitations", limit=3, sources=["arxiv"])
    target_paper = next((p for p in results if p.pdf_url), None)
    if not target_paper:
        print("No papers with PDFs found.")
        return
        
    paper_id = FetcherManager.build_stable_paper_id(
        doi=target_paper.doi, title=target_paper.title, 
        year=target_paper.year, source=target_paper.source
    )
    
    print(f"\n2. Downloading: {target_paper.title} (ID: {paper_id})")
    dl_resp = await downloader.download_pdf(
        pdf_url=target_paper.pdf_url, paper_id=paper_id,
        source=target_paper.source, title=target_paper.title, year=target_paper.year
    )
    
    print("\n3. Extracting and parsing sections...")
    ext_resp = extractor.extract_and_process(local_pdf_path=Path(dl_resp.local_path), paper_id=paper_id, parse_sections=True)
    
    print(f"\n4. Mining Gap Signals...")
    mine_resp = gap_service.process_mining_request(
        paper_ids=[paper_id],
        processed_sections_paths=None,
        top_k=10,
        include_sections=None,
        save=True
    )
    
    print(f"\n--- MINING SUCCESS ({mine_resp.count} signals found) ---")
    print(f"Saved to: {mine_resp.results_path}")
    print("\nTOP 10 SIGNALS:")
    for i, sig in enumerate(mine_resp.signals):
        print(f"{i+1}. [Score: {sig.score}] [Pattern: {sig.pattern}] [Section: {sig.section}]")
        print(f"   {sig.sentence}")
        print()

if __name__ == "__main__":
    asyncio.run(main())
