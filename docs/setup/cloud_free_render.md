# Cloud Deployment: Free-Tier (Supabase + Render)

This guide describes how to deploy the AI Research Gap Identifier completely free, without relying on Render's paid persistent disks, by using Supabase for the database, vector storage, and artifact storage.

## Architecture

- **Backend**: Render (Free Tier Web Service, stateless).
- **Frontend**: Vercel (Free Tier, static SPA).
- **Database**: Supabase PostgreSQL (Free Tier).
- **Vector Storage**: Supabase pgvector (Free Tier).
- **Artifact Storage**: Supabase Storage buckets (Free Tier).

By enabling the Supabase integration flags, the backend will no longer require local disk persistence for ChromaDB vectors, SQLite databases, or downloaded PDFs. Everything is pushed to Supabase.

## 1. Supabase Setup

### Database & pgvector
1. Create a new Supabase Project.
2. In the Supabase SQL Editor, enable the `vector` extension and create the tables. (Our SQLAlchemy models will auto-create the tables, but `pgvector` requires manual extension activation):
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

### Storage Bucket
1. Navigate to **Storage** in the Supabase Dashboard.
2. Create a new bucket named **`documents`**.
3. *Recommendation:* Make the bucket **Public** if you want easy downloads for end-users on the frontend. Otherwise, keep it private and the backend will manage access.

## 2. Environment Configuration

You must provide the following environment variables to your Render Backend:

```env
# Enable Supabase features
VECTOR_BACKEND=pgvector
ARTIFACT_BACKEND=supabase

# Supabase Credentials
SUPABASE_URL=https://<your-project>.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<your-service-role-key> # Needed to bypass RLS for uploads
DATABASE_URL=postgresql+psycopg://postgres.xxx:password@aws-0-region.pooler.supabase.com:6543/postgres

# Other existing keys
GROQ_API_KEY=gsk_...
ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

> [!WARNING]
> Do **NOT** use your `anon` key for `SUPABASE_SERVICE_ROLE_KEY`. The backend needs the service role key to forcefully upload files to the bucket without dealing with Row Level Security (RLS) policies.

## 3. Deployment

Once your environment variables are configured on Render:
1. The system will start as a stateless container.
2. When a user requests a pipeline run, the PDFs are downloaded temporarily to the Render container.
3. Once processed, the PDFs, raw texts, and Markdown reports are uploaded to Supabase Storage.
4. Vector embeddings are upserted into the `paper_section_vectors` PostgreSQL table using `pgvector`.
5. The container can safely restart or sleep without losing any data!
