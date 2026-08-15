# Supabase Setup Guide

To successfully migrate the AI Research Gap Identifier to a stateless architecture (Option A), your Supabase Database must be initialized properly.

## 1. Vector Database Configuration (pgvector)

You must enable the vector extension in your Postgres instance before applying the Alembic migrations.

### SQL Setup

Run the following inside the **Supabase SQL Editor**:

```sql
-- Enable the pgvector extension to calculate embeddings
CREATE EXTENSION IF NOT EXISTS vector;
```

### Table Architecture

Once the extension is enabled, the Alembic migration script will automatically construct the vectors table. The table schema equates to:

```sql
CREATE TABLE paper_section_vectors (
    id VARCHAR PRIMARY KEY,
    paper_id VARCHAR NOT NULL,
    text VARCHAR NOT NULL,
    embedding vector(384),
    metadata_json VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Note on Embedding Dimension**: The dimension `384` is explicitly derived from the underlying PyTorch `sentence-transformers/all-MiniLM-L6-v2` model. Changing the embedding model would require dropping and migrating a new vector dimension mapping.

## 2. Storage Buckets (Supabase Storage)

Because the Render instance has ephemeral storage, all files are uploaded and persisted using Supabase Storage.

### Bucket Setup

1. Open your **Supabase Dashboard**.
2. Navigate to **Storage -> Create a new bucket**.
3. Name the bucket `documents`.
4. Ensure the bucket is designated as **Public** (Do NOT tick Private).

### Storage Architecture & Privacy Policies

- The system currently assumes a **Public** bucket.
- This allows the frontend application to generate static downloadable URLs directly to user artifacts (such as PDF viewing or downloading the Gap Report generated Markdown file).
- Bypassing Row Level Security (RLS): The backend application performs internal file uploads using the `SUPABASE_SERVICE_ROLE_KEY` to securely push to the bucket without being restricted by complex RLS configurations.
