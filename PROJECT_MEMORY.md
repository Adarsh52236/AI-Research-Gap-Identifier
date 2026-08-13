# Project Memory

## Phase Tracking
| Phase | Status |
|-------|--------|
| Phase 1: Document Fetching | Pending |
| Phase 2: Text Extraction | Pending |
| Phase 3: User Input & Intent | Pending |
| Phase 4: NLP Processing | Pending |
| Phase 5: Embeddings & Vector Search | Pending |
| Phase 6: Topic Modeling | Pending |
| Phase 7: LLM Gap Reasoning | Pending |
| Phase 8: Report & UI | Pending |
| Phase 9: Testing & Deployment | Pending |
\n- 2026-08-13: Phase 1A implemented: health + search\n  - Proof instructions:\n    - `curl http://localhost:8000/api/v1/health/`\n    - `curl -X POST http://localhost:8000/api/v1/search/ -H "Content-Type: application/json" -d '{"query":"AI research gaps","limit":5}'`\n    - `pytest backend/tests -q`\n    - `set PYTHONPATH=. && python -m backend.scripts.manual_search_test`\n\n- 2026-08-14: Phase 1B implemented: local-first PDF downloader\n  - Added `/api/v1/papers/download/` endpoint\n  - Proof instructions:\n    - `curl -X POST http://localhost:8000/api/v1/papers/download/ -H "Content-Type: application/json" -d '{"pdf_url":"http://arxiv.org/pdf/2101.00001","paper_id":"2101_00001","source":"arxiv","year":2024}'`\n    - `pytest backend/tests -q`\n    - `set PYTHONPATH=. && python backend/scripts/manual_download_test.py`\n\n- 2026-08-14: Phase 2A implemented: PDF Extraction and Section Parsing\n  - Added `/api/v1/papers/extract/` endpoint\n  - Proof instructions:\n    - `pytest backend/tests -q`\n    - `PYTHONPATH=. python backend/scripts/manual_extract_test.py`\n\n- 2026-08-14: Phase 3 implemented: Deterministic Gap Signal Mining\n  - Added `/api/v1/analysis/gap-signals/` endpoint\n  - Proof instructions:\n    - `pytest backend/tests -q`\n    - `PYTHONPATH=. python backend/scripts/manual_gap_signals_test.py`\n\n- 2026-08-14: Phase 4 implemented: Semantic Memory (ChromaDB + sentence-transformers)\n  - Added `/api/v1/analysis/index-embeddings/` and `/api/v1/analysis/similarity-search/` endpoints\n  - Proof instructions:\n    - `pytest backend/tests -q`\n    - `PYTHONPATH=. python backend/scripts/manual_embeddings_test.py`\n\n- 2026-08-14: Phase 5 implemented: Groq LLM Gap Report Generator\n  - Added `/api/v1/analysis/gap-report/` endpoint\n  - Proof instructions:\n    - `pytest backend/tests -q`\n    - `PYTHONPATH=. python backend/scripts/manual_gap_report_test.py`\n