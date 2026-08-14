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

- 2026-08-13: Phase 1A implemented: health + search
  - Proof instructions:
    - `curl http://localhost:8000/api/v1/health/`
    - `curl -X POST http://localhost:8000/api/v1/search/ -H "Content-Type: application/json" -d '{"query":"AI research gaps","limit":5}'`
    - `pytest backend/tests -q`
    - `set PYTHONPATH=. && python -m backend.scripts.manual_search_test`

- 2026-08-14: Phase 1B implemented: local-first PDF downloader
  - Added `/api/v1/papers/download/` endpoint
  - Proof instructions:
    - `curl -X POST http://localhost:8000/api/v1/papers/download/ -H "Content-Type: application/json" -d '{"pdf_url":"http://arxiv.org/pdf/2101.00001","paper_id":"2101_00001","source":"arxiv","year":2024}'`
    - `pytest backend/tests -q`
    - `set PYTHONPATH=. && python backend/scripts/manual_download_test.py`

- 2026-08-14: Phase 2A implemented: PDF Extraction and Section Parsing
  - Added `/api/v1/papers/extract/` endpoint
  - Proof instructions:
    - `pytest backend/tests -q`
    - `PYTHONPATH=. python backend/scripts/manual_extract_test.py`

- 2026-08-14: Phase 3 implemented: Deterministic Gap Signal Mining
  - Added `/api/v1/analysis/gap-signals/` endpoint
  - Proof instructions:
    - `pytest backend/tests -q`
    - `PYTHONPATH=. python backend/scripts/manual_gap_signals_test.py`

- 2026-08-14 — Phase 3 quality improvements:
  - Added noise filtering (alpha ratio, tables/captions heuristics, citation artifacts) to prevent mining junk from PDFs.
  - Added section prioritization (FUTURE WORK > CONCLUSION > INTRODUCTION > full_text) to increase precision.
  - Added quality_score to GapSignal schema to rank highly-probable gap sentences above borderline ones.
  - Added robust tests for noise filtering since tables/captions were previously mistakenly mined.

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

- 2026-08-13: Phase 1A implemented: health + search
  - Proof instructions:
    - `curl http://localhost:8000/api/v1/health/`
    - `curl -X POST http://localhost:8000/api/v1/search/ -H "Content-Type: application/json" -d '{"query":"AI research gaps","limit":5}'`
    - `pytest backend/tests -q`
    - `set PYTHONPATH=. && python -m backend.scripts.manual_search_test`

- 2026-08-14: Phase 1B implemented: local-first PDF downloader
  - Added `/api/v1/papers/download/` endpoint
  - Proof instructions:
    - `curl -X POST http://localhost:8000/api/v1/papers/download/ -H "Content-Type: application/json" -d '{"pdf_url":"http://arxiv.org/pdf/2101.00001","paper_id":"2101_00001","source":"arxiv","year":2024}'`
    - `pytest backend/tests -q`
    - `set PYTHONPATH=. && python backend/scripts/manual_download_test.py`

- 2026-08-14: Phase 2A implemented: PDF Extraction and Section Parsing
  - Added `/api/v1/papers/extract/` endpoint
  - Proof instructions:
    - `pytest backend/tests -q`
    - `PYTHONPATH=. python backend/scripts/manual_extract_test.py`

- 2026-08-14: Phase 3 implemented: Deterministic Gap Signal Mining
  - Added `/api/v1/analysis/gap-signals/` endpoint
  - Proof instructions:
    - `pytest backend/tests -q`
    - `PYTHONPATH=. python backend/scripts/manual_gap_signals_test.py`

- 2026-08-14 — Phase 3 quality improvements:
  - Added noise filtering (alpha ratio, tables/captions heuristics, citation artifacts) to prevent mining junk from PDFs.
  - Added section prioritization (FUTURE WORK > CONCLUSION > INTRODUCTION > full_text) to increase precision.
  - Added quality_score to GapSignal schema to rank highly-probable gap sentences above borderline ones.
  - Added robust tests for noise filtering since tables/captions were previously mistakenly mined.

- 2026-08-14: Phase 4 implemented: Semantic Memory (ChromaDB + sentence-transformers)
  - Added `/api/v1/analysis/index-embeddings/` and `/api/v1/analysis/similarity-search/` endpoints
  - Proof instructions:
    - `pytest backend/tests -q`
    - `PYTHONPATH=. python backend/scripts/manual_embeddings_test.py`

- 2026-08-14: Phase 5 implemented: Groq LLM Gap Report Generator
  - Added `/api/v1/analysis/gap-report/` endpoint
  - Proof instructions:
    - `pytest backend/tests -q`
    - `PYTHONPATH=. python backend/scripts/manual_gap_report_test.py`

- 2026-08-14: Phase 5.1 implemented: Batch Pipeline Runner
  - Added a stateful pipeline runner to orchestrate search -> download -> extract -> mine -> index -> report automatically across multiple papers.
  - Implemented robust error handling per-paper and skipping/resume behaviors by inspecting disk/DB state.
  - Added endpoints `/api/v1/analysis/pipeline-run/` and local state tracking via `storage/runs/<run_id>/status.json` and `events.jsonl`.
  - Proof instructions:
    - `pytest backend/tests -q`
    - `PYTHONPATH=. python backend/scripts/manual_batch_pipeline_test.py`

- 2026-08-14: Phase 6 implemented: SQLAlchemy Persistence Layer
  - Added PostgreSQL/SQLite hybrid support via SQLAlchemy using `DATABASE_URL`.
  - Added ORM models: `Paper`, `DownloadArtifact`, `ExtractionArtifact`, `GapSignalRow`, `PipelineRunRow`, `ReportRow`.
  - Integrated graceful CRUD upserts into `PipelineRunner` that fallback to standard logging on DB failures.
  - Default tests seamlessly inject a fast, in-memory SQLite schema instance.
  - Proof instructions:
    - `pytest backend/tests/integration/test_db_persistence.py -q`

- 2026-08-14: Phase 7 implemented: React UI Frontend
  - Built a clean, minimalist "Claude-like" single-page application to drive the local research pipeline.
  - Features robust state management (Zustand with persistence), multipage routing (React Router), and comprehensive backend integration via Axios services.
  - Implemented `Landing` (minimal CTA), `ChatDashboard` (main app shell with ChatComposer and ChatThread), and `RunViewer` (view historical reports).
  - Used standard Vite + Tailwind CSS with a custom warm theme and dark mode toggling.
  - Supported rendering rich markdown reports with syntax highlighting, tables, and copy-to-clipboard functionality.
  - Proof instructions:
    - `cd frontend`
    - `npm run dev`
    - Visit `http://localhost:5173`

-- 2026-08-14: Phase 10 implemented: Publication Documentation & Paper Scaffold
  - Generated system architecture diagrams (`docs/architecture/system_design.md`).
  - Documented heuristic and semantic LLM synthesis methodology (`docs/methodology/methodology.md`).
  - Outlined experimental ablation modes (`docs/experiments/experiments.md`).
  - Detailed known systemic extraction and paywall constraints (`docs/limitations/limitations.md`).
  - Provided copy-paste reproducibility CLI guides (`docs/reproducibility/reproducibility.md`).
  - Drafted an ACL/NeurIPS-style Markdown paper scaffold (`docs/research_paper/draft.md`).
  - Implemented `backend/scripts/export_run_artifacts.py` to zip run evidence for supplementary attachments.

### Paper Checklist
To successfully finish the research paper for publication, complete the following items:
- [ ] **Curate Dataset**: Hand-label 50-100 high-quality gap signals inside `docs/eval/dataset_template.json` for Ground Truth.
- [ ] **Execute Ablation Study**: Run `ablation_runner.py` across all three modes (Heuristics, Heuristics+RAG, Heuristics+RAG+LLM).
- [ ] **Export Results**: Pipe output metrics from `eval_gap_signals.py` and `eval_gap_reports.py`.
- [ ] **Populate Tables**: Copy the precise metric outputs into Table 1 and Table 2 in `docs/research_paper/draft.md`.
- [ ] **Render Diagrams**: Ensure Mermaid diagrams compile beautifully via GitHub or Mermaid Live Editor for the final PDF submission.
- [ ] **Package Supplementary Material**: Run `export_run_artifacts.py <run_id>` for the best paper run and upload the `.zip` along with the paper.

- 2026-08-14: Phase 9 implemented: Deployment Hardening
  - Secured the app for production environments (Render/Vercel).
  - Environment-driven CORS configuration (`ALLOWED_ORIGINS`).
  - Added request/response robustness: `request_id` middleware, global exception formatting, structured logging.
  - Rate-limited expensive API endpoints using `slowapi`.
  - Added async `BackgroundTasks` execution option for the batch pipeline (`/api/v1/analysis/pipeline-run/?async_run=true`).
  - Bootstrapped GitHub Actions CI workflows for backend tests and frontend builds.
  - Documented deployment environment variables and commands in `README.md`.

### 2026-08-14 — Phase 8 completed (Evaluation Harness)
  - Created standardized `docs/eval` JSON templates (`dataset_template.json`, `labels_template.json`) for quantifying pipeline success.
  - Implemented automated core metrics `precision_at_k`, `recall_at_k`, and `f1` in `backend/app/core/eval/metrics.py`.
  - Implemented groundedness validation in `backend/app/core/eval/groundedness.py` capable of detecting missing/invalid citations and scoring textual relevance.
  - Added runner scripts (`eval_gap_signals.py`, `eval_gap_reports.py`) and an `ablation_runner.py` for structured paper experimentation.
  - Commands to run evaluations:
    - `PYTHONPATH=. python backend/scripts/eval_gap_signals.py docs/eval/dataset_template.json docs/eval/labels_template.json`
    - `PYTHONPATH=. python backend/scripts/eval_gap_reports.py <report_json> <evidence_texts_json>`
    - `PYTHONPATH=. python backend/scripts/ablation_runner.py ALL`
  - Planned Ablation Results Table Layout for Paper:
    | Configuration | Gap Precision@10 | Groundedness % | Hallucination % | Inter-Annotator Agmt |
    |---------------|------------------|----------------|-----------------|----------------------|
    | Mode A (Heur) | X%               | N/A            | N/A             | X%                   |
    | Mode B (H+V)  | Y%               | N/A            | N/A             | Y%                   |
    | Mode C (Full) | Z%               | A%             | B%              | Z%                   |

### 2026-08-14 — Phase 5 completed (LLM grounded gap report)
- Implemented Groq-based gap report generation with strict evidence-id citations and validation.
- End-to-end pipeline now supports: search → download → extract → gap signals → embeddings → similarity excerpts → Groq gap report (JSON + Markdown).
- Verified on real ArXiv paper; report saved under storage/reports/.
Next agenda: Final Polish.