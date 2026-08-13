"""Manual Download Test script."""
# How to run:
# activate venv
# python backend/scripts/manual_download_test.py

import asyncio
from backend.app.core.fetcher.fetcher_manager import FetcherManager
from backend.app.core.downloader.pdf_downloader import PDFDownloader

async def main():
    manager = FetcherManager()
    downloader = PDFDownloader()
    
    query = "graph neural networks"
    print(f"Searching ArXiv for: '{query}'...")
    
    results = await manager.search_all(
        query=query,
        limit=3,
        sources=["arxiv"]
    )
    
    target_paper = None
    for paper in results:
        if paper.pdf_url:
            target_paper = paper
            break
            
    if not target_paper:
        print("No papers with PDF URLs found in the top results.")
        return
        
    print(f"\nFound paper to download: {target_paper.title}")
    print(f"PDF URL: {target_paper.pdf_url}")
    
    paper_id = FetcherManager.build_stable_paper_id(
        doi=target_paper.doi,
        title=target_paper.title,
        year=target_paper.year,
        source=target_paper.source
    )
    
    print("\nDownloading...")
    try:
        response = await downloader.download_pdf(
            pdf_url=target_paper.pdf_url,
            paper_id=paper_id,
            source=target_paper.source,
            title=target_paper.title,
            year=target_paper.year
        )
        print(f"\nSuccess! File downloaded.")
        print(f"Local Path: {response.local_path}")
        print(f"Size: {response.size_bytes} bytes")
        print(f"SHA256: {response.sha256}")
    except Exception as e:
        print(f"\nDownload failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
