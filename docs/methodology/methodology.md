# Methodology

The AI Research Gap Identifier pipeline is composed of several deterministic data transformations followed by a bounded LLM synthesis step.

## 1. Corpus Acquisition
The pipeline begins by querying the arXiv API for papers within a specific domain and year range. Upon selection, the raw PDFs are downloaded into local storage (`storage/downloads`).

## 2. Structural Parsing
We utilize `PyMuPDF` to traverse the PDF document hierarchy. The extraction logic identifies standard research sections (e.g., Abstract, Introduction, Limitations, Conclusion) based on typographical heuristics. Text is then grouped by section, and noisy elements (such as tables or deeply formatted references) are scrubbed.

## 3. Heuristic Gap Mining
To maintain strict traceability, we avoid feeding entire raw PDFs into an LLM. Instead, we use a regex-based heuristic engine to score individual sentences.
- Patterns target terms like "future work should", "we leave it to", "a limitation is".
- Sentences matching patterns are flagged as "Gap Signals" and saved with contextual metadata in `gap_signals.json`.

## 4. Semantic Embedding
The parsed sections are chunked and vectorized using a lightweight embedding model (`sentence-transformers/all-MiniLM-L6-v2`) and stored persistently on disk using ChromaDB. This forms the semantic retrieval layer.

## 5. Grounded LLM Synthesis
For the final step, we provide a strict prompt to an LLM (via Groq API). The prompt includes:
1. The deterministic Gap Signals.
2. Vector-matched excerpts from the ChromaDB index that relate closely to the gap signals.
The LLM is constrained to only synthesize claims that cite the specific `evidence_id` provided, ensuring zero-hallucination tracking.
