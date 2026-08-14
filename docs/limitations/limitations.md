# Limitations

While the pipeline offers a scalable method for automated literature review, several inherent limitations must be acknowledged.

## 1. PDF Extraction Anomalies
Scientific PDFs are notoriously difficult to parse due to multi-column layouts, embedded figures, and non-standard typography.
- **PyMuPDF constraints**: Although we employ heuristic noise filters to strip references and tables, fragmented sentences crossing columns can occasionally be misparsed as broken strings, lowering downstream mining accuracy.

## 2. API Rate Limits & Paywalls
Our data ingestion relies heavily on open-access repositories like arXiv.
- **Rate Limits**: The arXiv API imposes strict rate limits on search queries. To mitigate this, our fetcher limits concurrent requests.
- **Paywalls**: Papers outside of open-access domains (e.g., specific IEEE or ACM articles without public PDFs) cannot be downloaded and analyzed by the current system, limiting the overall scope of the gap reports.

## 3. Heuristic Rigidity
The Gap Signal Miner (Phase 3) relies on deterministic regex patterns (e.g., "we leave it to future work").
- **False Negatives**: If an author expresses a limitation creatively or subtly, the regex engine will miss it, leading to lower recall. We mitigate this by using RAG in Phase 5 to provide broader semantic context to the LLM.

## 4. LLM Prompt Sensitivity
The final report generation utilizes Groq models (`llama-3.3-70b-versatile`). 
- **Instruction Following**: Despite strict prompting to avoid hallucinations and require citation IDs, LLMs can occasionally "smooth over" citations or drop IDs entirely if the generated sentence structure becomes too complex. Our `groundedness.py` evaluation script actively flags and penalizes these occurrences.
