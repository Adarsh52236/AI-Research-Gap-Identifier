"""Manual extraction test script."""
# Run with: PYTHONPATH=. python backend/scripts/manual_extract_test.py
import sys
import asyncio
import json
from pathlib import Path
from backend.app.core.fetcher.fetcher_manager import FetcherManager
from backend.app.core.downloader.pdf_downloader import PDFDownloader
from backend.app.core.extractor.extraction_service import ExtractionService

sys.stdout.reconfigure(encoding='utf-8')

async def main():
    manager = FetcherManager()
    downloader = PDFDownloader()
    extractor = ExtractionService()
    
    print("1. Searching ArXiv for a paper...")
    results = await manager.search_all(query="LLM hallucination", limit=3, sources=["arxiv"])
    target_paper = next((p for p in results if p.pdf_url), None)
    if not target_paper:
        print("No papers with PDFs found.")
        return
        
    print(f"\n2. Downloading: {target_paper.title}")
    paper_id = FetcherManager.build_stable_paper_id(
        doi=target_paper.doi, title=target_paper.title, 
        year=target_paper.year, source=target_paper.source
    )
    
    dl_resp = await downloader.download_pdf(
        pdf_url=target_paper.pdf_url, paper_id=paper_id,
        source=target_paper.source, title=target_paper.title, year=target_paper.year
    )
    
    local_path = Path(dl_resp.local_path)
    print(f"Downloaded to {local_path}")
    
    print("\n3. Extracting and parsing sections...")
    ext_resp = extractor.extract_and_process(local_pdf_path=local_path, paper_id=paper_id, parse_sections=True)
    
    print(f"\n--- EXTRACTION SUCCESS ---")
    print(f"Extracted Path: {ext_resp.raw_text_path}")
    print(f"Sections Path: {ext_resp.sections_path}")
    print(f"Sections Found: {ext_resp.sections_found}")
    
    with open(ext_resp.sections_path, "r", encoding="utf-8") as f:
        sections = json.load(f)
        
    if "ABSTRACT" in sections:
        print("\n--- ABSTRACT (First 300 chars) ---")
        print(sections["ABSTRACT"][:300] + "...")
    else:
        print("\n--- FULL TEXT (First 300 chars) ---")
        print(sections["full_text"][:300] + "...")

if __name__ == "__main__":
    asyncio.run(main())
