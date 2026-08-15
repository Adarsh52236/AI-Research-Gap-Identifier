# AI Research Gap Identifier

![Backend Tests](https://github.com/Adarsh52236/AI-Research-Gap-Identifier/actions/workflows/run_tests.yml/badge.svg)
![Frontend Build](https://github.com/Adarsh52236/AI-Research-Gap-Identifier/actions/workflows/frontend_build.yml/badge.svg)

An AI-powered pipeline to search, download, parse, and analyze scientific papers from arXiv to extract and synthesize "research gaps" (limitations, future work).

## Deployment

### Live URLs
- **Frontend (Vercel)**: `https://<your-vercel-domain>`
- **Backend (Render)**: `https://ai-research-gap-identifier-backend.onrender.com`
*(Update these placeholders with your actual live URLs after deployment)*

### Cloud Setup Guide
For comprehensive step-by-step instructions on deploying to Render and Vercel, attaching persistent disks, configuring SPA rewrites, and setting up GitHub Actions CI/CD, please refer to the [Cloud Deployment Guide](docs/setup/cloud_deployment.md).

### Deploy Checklist
- [ ] Connect repository to Render and deploy from `render.yaml` blueprint.
- [ ] Ensure Render persistent disk is attached.
- [ ] Connect repository to Vercel, set root directory to `frontend`.
- [ ] Ensure Vercel `VITE_API_BASE_URL` env variable points to Render.
- [ ] Push to `main` to trigger GitHub Actions CI pipeline.

## Windows Setup Instructions
Run `scripts\setup.bat` to set up the environment.

## How to run locally
- Frontend: `cd frontend && npm run dev`
- Backend: `cd backend && uvicorn app.main:app --reload`

### UI Architecture & Endpoints
The frontend is a "Claude-like" application mapping directly to the backend batch pipeline.
- Start run: `POST /api/v1/analysis/pipeline-run/?async_run=true`
- Poll status: `GET /api/v1/analysis/pipeline-run/{runId}`
- View report: `GET /api/v1/analysis/pipeline-run/{runId}/report`
- History: `GET /api/v1/analysis/runs` (Supports graceful DB fallback to local files).

### Theme Tokens
The frontend features a warm, paper-like theme built on CSS variables inside `frontend/src/styles/index.css`.
- `--bg`: Main background color
- `--panel`: Surface color for sidebars and composers
- `--accent`: Core interactive color (terracotta/rust)
- `--text`: Base text color

## Environment variables
Check `.env.example` in both `frontend` and `backend` directories.
