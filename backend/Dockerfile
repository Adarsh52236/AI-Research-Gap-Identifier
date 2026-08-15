FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (e.g., for PyMuPDF or compiling extensions if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libmupdf-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY . ./backend/

ENV PYTHONPATH=/app

# Use $PORT provided by Render, defaulting to 8000
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
