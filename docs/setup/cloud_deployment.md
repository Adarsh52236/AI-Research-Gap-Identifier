# Cloud Deployment Setup

This document provides step-by-step instructions for deploying the AI Research Gap Identifier across Render (Backend) and Vercel (Frontend).

## 1. Backend Deployment (Render)

We use Render's Blueprint (`render.yaml`) to automatically configure the backend environment.

### Steps:
1. Go to the [Render Dashboard](https://dashboard.render.com/).
2. Click **New** -> **Blueprint**.
3. Connect your GitHub repository.
4. Render will read the `render.yaml` file in the root of the repository and prompt you to create the `ai-research-gap-identifier-backend` web service.
5. Provide the required secrets when prompted:
   - `GROQ_API_KEY`: Your Groq API key for LLM integration.
   - `DATABASE_URL`: (Optional) Your PostgreSQL connection string.
6. The blueprint automatically provisions a **10GB persistent disk** mounted at `/opt/render/project/src/backend/storage` to preserve SQLite databases, ChromaDB vectors, and PDF artifacts.

## 2. Frontend Deployment (Vercel)

Vercel hosts the React SPA.

### Steps:
1. Go to the [Vercel Dashboard](https://vercel.com/dashboard).
2. Click **Add New** -> **Project**.
3. Import your GitHub repository.
4. In the configuration settings, set the **Root Directory** to `frontend`.
5. Expand the **Environment Variables** section and add:
   - `VITE_API_BASE_URL`: The URL of your deployed Render backend (e.g., `https://ai-research-gap-identifier-backend.onrender.com`).
6. Click **Deploy**.

> [!NOTE]
> We have included a `vercel.json` file in the frontend directory that automatically applies an SPA rewrite (`/(.*)` -> `/index.html`) to ensure React Router works seamlessly across page refreshes.

## 3. CI/CD via GitHub Actions

This repository includes a full CI/CD pipeline in `.github/workflows/`.

### CI (`ci.yml`)
Runs automatically on every push or pull request to the `main` or `dev` branches:
- **Backend**: Installs dependencies and runs `pytest` checks.
- **Frontend**: Runs `npm ci` and `npm run build` to ensure the UI compiles successfully.

### CD (`deploy.yml`)
(Optional) If you have disabled auto-deployments on Render/Vercel and wish to trigger them only when CI passes, you can use the deploy workflow.
- Requires adding `RENDER_DEPLOY_HOOK_URL` and `VERCEL_DEPLOY_HOOK_URL` to your GitHub Repository Secrets.
- Triggers via `curl POST` webhooks.

## Troubleshooting

### Vercel 404 on Page Refresh
If you manually deploy the frontend and receive a 404 error on refresh, verify that Vercel is reading the `frontend/vercel.json` file. Ensure your **Root Directory** in Vercel is set to `frontend`.

### Render Losing Files or Database Wiped
Render's filesystem is ephemeral. If files are being lost, verify that the persistent disk is attached to the service. The blueprint handles this by mounting a disk to `/opt/render/project/src/backend/storage`. Make sure all environment variables (`CHROMA_DB_PATH`, `STORAGE_DIR`, etc.) point to this mounted path (as pre-configured in `render.yaml`).
