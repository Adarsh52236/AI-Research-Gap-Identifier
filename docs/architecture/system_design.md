# System Design & Architecture

The AI Research Gap Identifier is a robust, local-first pipeline designed to ingest unstructured scientific PDFs and deterministically output grounded research gaps.

## Component Architecture

```mermaid
graph TD
    subgraph Frontend
        UI[React + Zustand]
        Axios[Axios Service Layer]
    end

    subgraph Backend FastAPI
        API[FastAPI Routers]
        Pipeline[Batch Pipeline Runner]
        
        subgraph Core Modules
            Fetcher[ArXiv Fetcher]
            Downloader[PDF Downloader]
            Extractor[PyMuPDF Extractor]
            Miner[Regex Gap Miner]
            Embedder[SentenceTransformers]
            Report[Groq LLM Synthesizer]
        end
    end

    subgraph Data Layer
        DB[(SQLite / Postgres)]
        VDB[(ChromaDB)]
        Disk[Local Disk Storage]
    end
    
    UI -->|HTTP POST| API
    API --> Pipeline
    Pipeline --> Fetcher
    Pipeline --> Downloader
    Pipeline --> Extractor
    Pipeline --> Miner
    Pipeline --> Embedder
    Pipeline --> Report
    
    Fetcher --> DB
    Downloader --> Disk
    Extractor --> Disk
    Miner --> Disk
    Embedder --> VDB
    Report --> Disk
```

## Request Lifecycle Sequence

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant FastAPI
    participant LocalDB
    participant ArXiv
    participant GroqLLM
    
    User->>Frontend: Enter query "KV Cache"
    Frontend->>FastAPI: POST /api/v1/search
    FastAPI->>ArXiv: Fetch paper metadata
    ArXiv-->>FastAPI: Atom feed xml
    FastAPI-->>Frontend: Paper List
    
    User->>Frontend: Click "Run Pipeline"
    Frontend->>FastAPI: POST /api/v1/analysis/pipeline-run (async)
    FastAPI-->>Frontend: Returns run_id (Pending)
    
    FastAPI->>FastAPI: BackgroundTask
    FastAPI->>ArXiv: Download PDF
    FastAPI->>LocalDB: Store DownloadArtifact
    FastAPI->>FastAPI: Extract text & structure
    FastAPI->>FastAPI: Regex Mine top sentences
    FastAPI->>FastAPI: Vectorize text (ChromaDB)
    FastAPI->>GroqLLM: Synthesize Gap Report (grounded)
    GroqLLM-->>FastAPI: Structured JSON report
    FastAPI->>LocalDB: Store ReportRow & Markdown
    
    Frontend->>FastAPI: Poll /pipeline-run/{run_id}
    FastAPI-->>Frontend: Status: Completed
```
