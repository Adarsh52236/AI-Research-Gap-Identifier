"""Manual Search Test script."""
# How to run:
# Set PYTHONPATH if needed, then:
# python -m backend.scripts.manual_search_test

import asyncio
from backend.app.core.fetcher.fetcher_manager import FetcherManager

async def main():
    manager = FetcherManager()
    query = "graph neural networks"
    print(f"Searching for: '{query}'...")
    
    results = await manager.search_all(
        query=query,
        limit=5,
        sources=["arxiv", "semantic_scholar"]
    )
    
    print(f"\nFound {len(results)} deduplicated results:\n")
    for idx, paper in enumerate(results[:5], 1):
        print(f"{idx}. {paper.title}")
        print(f"   Source: {paper.source}, Year: {paper.year}")
        print(f"   PDF: {paper.pdf_url}")
        print(f"   Abstract: {paper.abstract[:100] if paper.abstract else 'N/A'}...\n")

if __name__ == "__main__":
    asyncio.run(main())
