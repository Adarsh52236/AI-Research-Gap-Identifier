"""Manual test for embeddings pipeline."""
# Run with: PYTHONPATH=. python backend/scripts/manual_embeddings_test.py
import sys
import asyncio
from pathlib import Path
from backend.app.core.fetcher.fetcher_manager import FetcherManager
from backend.app.core.downloader.pdf_downloader import PDFDownloader
from backend.app.core.extractor.extraction_service import ExtractionService
from backend.app.core.embeddings.indexing_service import EmbeddingIndexingService
from backend.app.core.embeddings.similarity_search import SimilaritySearchService

sys.stdout.reconfigure(encoding='utf-8')

async def main():
    manager = FetcherManager()
    downloader = PDFDownloader()
    extractor = ExtractionService()
    indexer = EmbeddingIndexingService()
    searcher = SimilaritySearchService()
    
    print("1. Searching...")
    results = await manager.search_all(query="high concurrency LLM KV cache memory", limit=3, sources=["arxiv"])
    target = next((p for p in results if p.pdf_url), None)
    if not target: return
        
    pid = FetcherManager.build_stable_paper_id(target.doi, target.title, target.year, target.source)
    print(f"\n2. Downloading {target.title}...")
    dl = await downloader.download_pdf(target.pdf_url, pid, target.source, target.title, target.year)
    
    print("\n3. Extracting sections...")
    ext = extractor.extract_and_process(Path(dl.local_path), pid, True)
    
    print("\n4. Indexing (may download sentence-transformers model)...")
    idx_count, skip_count = indexer.index_from_sections_json(
        Path(ext.sections_path), pid, target.source, target.year, target.title,
        ["ABSTRACT", "INTRODUCTION", "CONCLUSION"], force_reindex=True, save_text=True
    )
    print(f"Indexed: {idx_count}, Skipped: {skip_count}")
    
    print("\n5. Querying...")
    res = searcher.search("How to optimize KV cache?", 5, None, None, None, None)
    
    print(f"\n--- RESULTS ({res.count}) ---")
    for r in res.results:
        print(f"[Score: {r.score}] Section: {r.section}\n{r.preview}\n")

if __name__ == "__main__":
    asyncio.run(main())
