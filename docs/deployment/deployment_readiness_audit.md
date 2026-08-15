# Deployment Readiness Audit Report

This document serves as a comprehensive audit of the AI Research Gap Identifier's readiness for a fully stateless deployment using Render (Free Tier) for the backend and Vercel for the frontend.

## SECTION A — Current Implementation Status

### VECTOR_BACKEND Support
- **chroma**: ✅ Supported (Default local fallback)
- **pgvector**: ✅ Supported (Production vector engine)
- **Implementation Mapping**: 
  - Regulated via `VECTOR_BACKEND` env var in `backend/app/config.py`
  - Handled by `get_vector_store()` factory in `backend/app/core/embeddings/vector_store.py`
  - Instantiates `ChromaVectorStore` or `PgVectorStore` (in `pgvector_store.py`) dynamically.

### ARTIFACT_BACKEND Support
- **local**: ✅ Supported (Local disk storage)
- **supabase storage**: ✅ Supported (Cloud bucket storage)
- **Implementation Mapping**:
  - Regulated via `ARTIFACT_BACKEND` env var.
  - Handled by `get_artifact_store()` factory in `backend/app/core/storage/artifact_store.py`
  - Instantiates `LocalArtifactStore` or `SupabaseStorageStore`.
- **Uploaded Artifacts**:
  - Raw PDFs (`{paper_id}.pdf`)
  - Extracted Text (`{paper_id}_raw.txt`)
  - Sections JSON (`{paper_id}_sections.json`)
  - Gap Reports (`{report_id}.md`)
  - Note: Run Logs (`status.json` and `events.jsonl`) are currently NOT explicitly uploaded to Supabase but are instead persisted to Postgres within the `runs` table payload.

### DB Persistence
- **DATABASE_URL Usage**: ✅ Verified. Used by `backend/app/db/database.py` via SQLAlchemy.
- **Models Created/Migrated**: ✅ Verified. Latest alembic migration (`06a7ec88d702`) applies the schema.
- **Required Tables**:
  - `users` (Authentication tracking)
  - `papers` (Core metadata)
  - `download_artifacts` (Download records & paths)
  - `extraction_artifacts` (Extraction state & paths)
  - `mining_jobs` (Gap signal mining status)
  - `reports` (Final report generations & paths)
  - `paper_section_vectors` (pgvector 384-dimensional storage for chunks)
  - `runs` (Pipeline tracking status payloads)

### PipelineRunner Cloud Readiness
- **Resume/Skip Logic**: ✅ Verified. `PipelineRunner` successfully leverages the Database Run status and existing artifacts to skip previously completed stages if rerun.
- **Cloud-Safe Behavior**: ✅ Verified. The Pipeline completely offloads binary persistence via `ArtifactStore` when `ARTIFACT_BACKEND=supabase` is set, making it fully stateless.

### Frontend Deployment
- **Environment Usage**: ✅ Verified. Consumes `VITE_API_BASE_URL` properly in Axios and router requests.
- **SPA Rewrite**: ✅ Verified. `frontend/vercel.json` natively contains the wildcard `/(.*)` -> `/index.html` rewrite rules.

---

## SECTION B — Required Environment Variables

### Backend (Render Free Tier)
| Variable | Example Value | Required? | Usage Location |
|---|---|---|---|
| `DATABASE_URL` | `postgresql+psycopg://postgres.../postgres` | **Yes** | `backend/app/db/database.py` |
| `SUPABASE_URL` | `https://xyz.supabase.co` | **Yes** (If pgvector) | `pgvector_store.py`, `supabase_storage_store.py` |
| `SUPABASE_SERVICE_ROLE_KEY` | `eyJhbGci...` | **Yes** (If Supabase Storage) | `pgvector_store.py`, `supabase_storage_store.py` |
| `SUPABASE_ANON_KEY` | `eyJhbGci...` | No | Not heavily used server-side |
| `GROQ_API_KEY` | `gsk_abc123...` | **Yes** | `llm_client.py` |
| `ALLOWED_ORIGINS` | `https://my-app.vercel.app` | **Yes** | `main.py` (CORS middleware) |
| `VECTOR_BACKEND` | `pgvector` | **Yes** | `vector_store.py` |
| `ARTIFACT_BACKEND` | `supabase` | **Yes** | `artifact_store.py` |
| `EMBEDDING_MODEL_NAME` | `sentence-transformers/all-MiniLM-L6-v2` | No (Defaults) | `embedding_generator.py` |
| `EMBEDDING_DEVICE` | `cpu` | No (Defaults) | `embedding_generator.py` |
| `CHROMA_DB_PATH` | `./storage/chromadb` | No (Ignored) | `vector_store.py` (Ignored if pgvector) |
| `ENVIRONMENT` | `production` | **Yes** | `config.py` |

### Frontend (Vercel)
| Variable | Example Value | Required? | Usage Location |
|---|---|---|---|
| `VITE_API_BASE_URL` | `https://my-render-app.onrender.com/api/v1` | **Yes** | Axios Base URL logic |

---

## SECTION C — Supabase Setup Verification

See [docs/deployment/supabase_setup.md](./supabase_setup.md) for full commands.
- **pgvector Extension Requirement**: Must execute `CREATE EXTENSION vector;` prior to running alembic migrations.
- **Table Name**: `paper_section_vectors`
- **Embedding Dimension**: `384` (Derived implicitly from the output vector length of `sentence-transformers/all-MiniLM-L6-v2`).
- **Storage Buckets Required**: `documents`
- **Bucket Privacy assumptions**: **Public**. Currently, the system uses public buckets to serve download links for reports and PDFs to the frontend client without requiring signed URL rotation. 

---

## SECTION D — Render FREE-Tier Deployment Plan (Stateless)

- **Persistent Disk Dependency**: **No persistent disk is required.**
- **Code Assumptions**: `PipelineRunner` checks `ARTIFACT_BACKEND` strictly. When `supabase`, no assumption is made about local storage persisting beyond the execution context. Local scratchpads/tempfiles are cleaned up post-upload.
- **Health Check Path**: `/api/v1/health/`
- **Render Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

See `.github/workflows/deploy.yml` for automated sync or the `render.yaml` configuration.

---

## SECTION E — Vercel Deployment Plan

- **Root Directory**: `frontend`
- **SPA Routing Rewrite Verification**: `frontend/vercel.json` provides comprehensive wildcard rewrites.
- See [docs/deployment/vercel_setup.md](./vercel_setup.md) for full dashboard instructions.

---

## SECTION F — CI/CD Verification

- **CI Workflow Status**: ✅ `ci.yml` exists. Checks `pytest backend/tests` and `npm run build` on `dev` and `main` branches.
- **CD Deploy Hook Status**: ❌ Needs verification (Typically Render natively handles deployment webhooks when hooked to main).
- See [docs/deployment/github_actions.md](./github_actions.md) for Branch Protection policies to enforce CI hooks.

---

## SECTION G — Risk & Fix List

### 1. Vector Dimension Mismatch
- **Risk**: Migrating from an alternative local embedding model to `all-MiniLM-L6-v2` in production can trigger PostgreSQL insertion errors (`expected 384 dimensions, got 768`).
- **Fix**: The `PaperSectionVector` model explicitly enforces `Vector(384)`. Ensure `EMBEDDING_MODEL_NAME` on Render is rigorously locked to the default value.

### 2. Rate Limiting / 429 Semantic Scholar
- **Risk**: Overloading the Semantic Scholar API with rapid pipeline searches triggers IP 429 Bans.
- **Fix**: The `SemanticScholarFetcher` integrates `asyncio.sleep()` retry headers to delay requests gracefully upon 429 detection.

### 3. Long-Running Pipeline HTTP Timeout Issues
- **Risk**: Free Tier Render instances drop HTTP requests after 60-100 seconds, while long gap analysis pipelines take 2-4 minutes.
- **Fix**: The pipeline heavily supports **background modes** natively (`/api/v1/analysis/pipeline-run/`). The frontend polls for `status.json` states rather than awaiting the master HTTP pipe.

### 4. Service Role Key Exposure Risk
- **Risk**: Accidental leakage of `SUPABASE_SERVICE_ROLE_KEY` to the Vercel Frontend bundle.
- **Fix**: Double check Vercel environment variables do not include Supabase secrets. `SUPABASE_SERVICE_ROLE_KEY` should solely exist in Render.

### 5. LLM Cost/Timeouts
- **Risk**: Large PDFs causing massive Groq context window ingestions, leading to API timeouts or quota ceilings.
- **Fix**: Handled by setting rigorous limits during extraction and `REPORT_TOP_K_GAPS` configuration bounds.

---
**Audit Generated via Automated Review Script**
