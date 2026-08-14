# Reproducibility Guide

This guide provides the exact commands needed for independent researchers to clone this repository, install the environment, and execute the full AI Research Gap Identifier pipeline from scratch on a local Windows machine.

## Prerequisites
- Windows 10/11
- Python 3.11+
- Node.js v20+

## 1. Environment Setup

Clone the repository and set up the backend environment:
```powershell
git clone https://github.com/Adarsh52236/AI-Research-Gap-Identifier.git
cd AI-Research-Gap-Identifier

# Set up Python virtual environment
python -m venv venv
.\venv\Scripts\activate
pip install -r backend/requirements.txt
```

Set up the `.env` file in the `backend/` directory:
```env
GROQ_API_KEY=your_groq_api_key_here
DB_ENABLED=False
RATE_LIMIT_ENABLED=False
```

## 2. Running a Manual End-to-End Test

To quickly verify that the pipeline can search, download, parse, and generate a report for a given topic, run the manual batch script:

```powershell
# Ensure PYTHONPATH is set so local modules resolve correctly
$env:PYTHONPATH="."

# Run the batch pipeline test for a specific domain
python backend/scripts/manual_batch_pipeline_test.py
```
This script performs the following:
1. Searches arXiv for the top 3 papers related to "KV Cache".
2. Downloads their PDFs.
3. Extracts text and parses sections.
4. Mines deterministic gap signals.
5. Indexes embeddings into a local ChromaDB instance.
6. Calls Groq to generate a final `report.md`.

Check `storage/reports/` for the synthesized output.

## 3. Running the Web Application

If you prefer to run the full UI:

### Start the Backend
```powershell
# In terminal 1
$env:PYTHONPATH="."
.\venv\Scripts\activate
uvicorn backend.app.main:app --reload --port 8000
```

### Start the Frontend
```powershell
# In terminal 2
cd frontend
npm install
npm run dev
```

Navigate to `http://localhost:5173` to use the interactive dashboard.

## 4. Running Evaluations
To reproduce the ablation study metrics and groundedness validation against the test dataset:

```powershell
$env:PYTHONPATH="."
python backend/scripts/ablation_runner.py
python backend/scripts/eval_gap_signals.py
python backend/scripts/eval_gap_reports.py
```
Outputs will be generated in standard output and logged to `docs/eval/`.
