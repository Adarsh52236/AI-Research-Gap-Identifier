# Vercel Deployment Guide (Frontend)

Deploying the React/Vite frontend to Vercel is extremely straightforward, provided you have configured your environment variables properly to point toward your Render backend.

## 1. Vercel Configuration & SPA Rewrite

This repository is already configured with `frontend/vercel.json`, which forces a Single-Page Application (SPA) wildcard rewrite strategy. 

```json
{
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

Because of this, React Router will correctly handle route resolution (`/app`, `/upload`, etc.) upon page refreshes, bypassing 404 errors.

## 2. Deployment Steps

1. Create a new Project in Vercel.
2. Link your GitHub repository.
3. **Framework Preset**: Vercel will auto-detect **Vite**.
4. **Root Directory**: You must explicitly set the Root Directory to `frontend`.
5. **Build Command**: Leave as `npm run build` (auto-detected).
6. **Output Directory**: Leave as `dist` (auto-detected).

## 3. Environment Variables

Under the Environment Variables section in Vercel, you must map the API endpoint to your backend application running on Render.

| Variable Name | Example Value | Description |
|---|---|---|
| `VITE_API_BASE_URL` | `https://ai-research-gap-identifier.onrender.com/api/v1` | **CRITICAL**: The fully qualified HTTP path to your Render backend `api/v1` route. |

> [!WARNING]
> Do **NOT** include trailing slashes in your `VITE_API_BASE_URL` (e.g. `.../api/v1/`).

> [!CAUTION]
> Do **NOT** put your Supabase or Groq keys into the Vercel dashboard. The frontend does not execute database queries natively. Exposing your `SUPABASE_SERVICE_ROLE_KEY` inside the client bundle is a severe security vulnerability.
