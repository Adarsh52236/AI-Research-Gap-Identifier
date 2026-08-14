# AI Research Gap Identifier

![Backend Tests](https://github.com/Adarsh52236/AI-Research-Gap-Identifier/actions/workflows/run_tests.yml/badge.svg)
![Frontend Build](https://github.com/Adarsh52236/AI-Research-Gap-Identifier/actions/workflows/frontend_build.yml/badge.svg)

An AI-powered pipeline to search, download, parse, and analyze scientific papers from arXiv to extract and synthesize "research gaps" (limitations, future work).

## Deployment

### Backend (Render / Railway)
1. Set the following environment variables:
   - `GROQ_API_KEY`: Your Groq API key
   - `ALLOWED_ORIGINS`: e.g. `https://your-frontend-domain.vercel.app`
   - `DATABASE_URL`: PostgreSQL connection string (Supabase)
   - `CHROMA_DB_PATH`: Set to a persistent disk path (e.g. `/opt/render/project/src/backend/storage/chromadb`)
2. Start command: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`

### Frontend (Vercel)
1. Point Vercel to the `frontend/` directory.
2. Build command: `npm run build`
3. Set Environment Variable:
   - `VITE_API_BASE_URL`: Your deployed backend URL (e.g. `https://my-backend.onrender.com`)


## Windows Setup Instructions
Run `scripts\setup.bat` to set up the environment.

## How to run separately
- Frontend: `cd frontend && npm run dev`
- Backend: `cd backend && uvicorn app.main:app --reload`

## Environment variables
Check `.env.example` in both `frontend` and `backend` directories.
