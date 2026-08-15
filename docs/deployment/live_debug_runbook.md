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

## Client-Side Debugging (VITE_DEBUG)

If the UI behaves unexpectedly and you need a deeper look at the network logs and polling lifecycle without combing through browser network tabs, you can enable our advanced client-side debugging toolkit.

### Enabling in Vercel
1. Go to your **Vercel Project Dashboard**.
2. Navigate to **Settings** > **Environment Variables**.
3. Add a new variable:
   - Key: `VITE_DEBUG`
   - Value: `true`
4. **Important**: You must trigger a new deployment for Vercel to bake this variable into the Vite build.

### Using the Debugger
Once deployed, open the application in your browser and open the Developer Tools Console.

- **Debug Panel:** A dark "DEBUG MODE" panel will appear anchored to the bottom of the screen. Clicking it reveals the exact backend URL the app is hitting, the last request details, active polling status, and formatted error messages.
- **Console Logs:** You will see highly structured, collapsed log groups for every API interaction.
  - `[API REQUEST] POST ...` shows the request payload, sanitized headers, and client request ID.
  - `[API RESPONSE] 200 ...` shows the elapsed response time and backend tracing headers (e.g. `X-Request-ID`, `X-Render-Origin-Server`).
  - `[API ERROR][HTTP_502]` explicitly categorizes backend failures vs CORS/Network drops, providing immediate context on *why* a failure occurred.
  - `[POLL START]`, `[POLL TICK]`, and `[POLL STOP]` clearly log the lifecycle of long-running pipeline polls, ensuring duplicate background loops are visually apparent.
