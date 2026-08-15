# Live Debug Runbook

This guide helps you diagnose and resolve production polling and pipeline errors, specifically on Render's Free Tier and Vercel.

## Interpreting Errors During Polling

### 502 Bad Gateway / 503 Service Unavailable / 504 Gateway Timeout
- **Symptom:** The frontend logs `AxiosError: Network Error` and displays "Temporary backend issue; retrying...".
- **Cause:** Render Free tier instances spin down after inactivity or crash under memory pressure. When waking up, requests may timeout (504) or connection drops (502).
- **Resolution:** The frontend is configured to slow down polling with exponential backoff (up to 15s) until the instance recovers. If it persists for minutes, check your Render dashboard logs. You can find the specific request using the `request_id` appended to API responses.

### 404 Run ID Not Found
- **Symptom:** The frontend displays "Run not found. Please restart analysis." and stops polling.
- **Cause:** The run status doesn't exist in the database. If this happens *intermittently*, the database connection might be failing. We fixed `DBRunStore` to raise a 500 error instead of returning `None` to distinguish this from an actual missing row.
- **Resolution:** If 404s still persist, verify that `DB_ENABLED=True` and `DATABASE_URL` is pointing to Supabase Postgres. If it falls back to local disk (SQLite or JSON files), the ephemeral nature of Render means disk contents are wiped on every deployment or restart.

## Running Smoke Tests

We have two python smoke tests to quickly verify the system health without triggering expensive LLM calls or large downloads. Both start a pipeline run with only the `search` step active.

### 1. Local Smoke Test
Verifies your local environment (`http://localhost:8001`).

```bash
# From the project root:
python backend/scripts/smoke_local.py
```
*Note: If local authentication is strictly enforced, you must provide a valid JWT token via `SMOKE_LOCAL_TOKEN` environment variable.*

### 2. Cloud Smoke Test
Verifies your live deployment on Render and Vercel.

```bash
# Linux/macOS
export CLOUD_BACKEND_BASE_URL="https://ai-research-gap-identifier-backend.onrender.com"
export CLOUD_EMAIL="test@example.com"
export CLOUD_PASSWORD="yourpassword"
python backend/scripts/smoke_cloud.py

# Windows (PowerShell)
$env:CLOUD_BACKEND_BASE_URL="https://ai-research-gap-identifier-backend.onrender.com"
$env:CLOUD_EMAIL="test@example.com"
$env:CLOUD_PASSWORD="yourpassword"
python backend/scripts/smoke_cloud.py
```

### 3. GitHub Action (Manual)
You can trigger the cloud smoke test manually via GitHub Actions.
1. Go to **Actions** > **Cloud Smoke Test**.
2. Click **Run workflow**.
3. Ensure your repository secrets (`CLOUD_BACKEND_BASE_URL`, `CLOUD_EMAIL`, `CLOUD_PASSWORD`) are correctly configured in GitHub Settings.

## Deep Health Endpoint
You can rapidly diagnose the DB and Supabase storage connection without starting a pipeline run:
```bash
curl https://ai-research-gap-identifier-backend.onrender.com/api/v1/health/deep
```
Expected response:
```json
{
  "status": "ok",
  "db_ok": true,
  "supabase_storage_ok": true,
  ...
}
```
