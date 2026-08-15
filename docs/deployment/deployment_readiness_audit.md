# Deployment Readiness Audit

## SECTION A — Current Implementation Status

### VECTOR_BACKEND Support
- **chroma**: ✅ Implemented (as legacy/local fallback)
- **pgvector**: ✅ Implemented
- **Where switching occurs**: `backend/app/core/embeddings/indexing_service.py` and `backend/app/core/embeddings/vector_store.py` rely on `settings.VECTOR_BACKEND`.

### ARTIFACT_BACKEND Support
- **local**: ✅ Implemented
- **supabase storage**: ✅ Implemented
- **Which artifacts are uploaded**:
  - PDFs (`downloads/` directory)
  - Raw extracted text (`processed/` directory)
  - Sections JSON (`processed/` directory)
  - Final Markdown Reports (`reports/` directory)
- **Where switching occurs**: `backend/app/core/storage/artifact_store.py` relies on `settings.ARTIFACT_BACKEND`.

### Pipeline Async / Polling
- **Does `/api/v1/analysis/pipeline-run/` fire-and-forget in production?**: ✅ Yes. When `ENVIRONMENT == "production"` or `async_run=True`, it returns the `run_id` immediately and executes the pipeline in FastAPI `BackgroundTasks`.
- **Is `DBRunStore` implemented to save steps to Postgres?**: ✅ Yes. `backend/app/core/pipeline/run_store.py` writes status and event streams to the `pipeline_runs` table via `DBRunStore`.
- **Does the frontend handle 404s cleanly?**: ✅ Yes. `ChatDashboard.jsx` implements exponential backoff polling, handling up to two consecutive 404s before gracefully failing.

---

## SECTION B — Missing / Pending for Deployment

### Render (Backend) FREE tier (Stateless)
- **Missing Env Vars Configuration in Render Dashboard**:
  Ensure the following variables are populated:
  - `DATABASE_URL` (Supabase Postgres Connection String)
  - `SUPABASE_URL`
  - `SUPABASE_SERVICE_ROLE_KEY`
  - `GROQ_API_KEY`
  - `VECTOR_BACKEND=pgvector`
  - `ARTIFACT_BACKEND=supabase`
  - `DB_ENABLED=true`
  - `ENVIRONMENT=production`
  - `ALLOWED_ORIGINS=https://<vercel-domain>`

### Vercel (Frontend)
- **Environment Variables**:
  - `VITE_API_BASE_URL` (Must point to the Render backend URL, e.g., `https://<your-render-app>.onrender.com/api/v1`)
- **Missing Items**:
  - No code changes missing. It is fully ready for deployment.

---

## SECTION C — Critical Bugs / Risks

### 1. Data Loss & Ephemeral Storage
- **Risk**: Render Free Tier spinning down causing data loss.
- **Mitigation**: Fixed. All artifacts are pushed to Supabase Storage, run streams are pushed to Postgres, and embeddings are in `pgvector`.
- **Status**: ✅ Resolved.

### 2. Dimension Mismatches
- **Risk**: `pgvector` index dimension must match the embedding model exactly. The model `all-MiniLM-L6-v2` produces `384`-dimensional embeddings.
- **Mitigation**: The `paper_section_vectors` table was initialized with `vector(384)`. If the model is ever changed (e.g., to OpenAI `text-embedding-3-small`), a new table or dimension migration will be required.
- **Status**: ✅ Acknowledged & Safe for current model.

### 3. Missing Env Vars
- **Risk**: If `ENVIRONMENT` is missing, it defaults to `development`, meaning the pipeline runs synchronously, which might cause Render to timeout the HTTP request on long gaps analyses.
- **Mitigation**: Added `ENVIRONMENT` defaulting logic, but highly recommended to explicitly set `ENVIRONMENT=production` in Render.

### 4. Security Leaks
- **Risk**: `SUPABASE_SERVICE_ROLE_KEY` is highly privileged.
- **Mitigation**: Kept purely on the backend, passed as an environment variable. Not exposed to the frontend.
- **Status**: ✅ Safe.
