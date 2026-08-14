# Experimental Design

To scientifically validate our extraction quality and report groundedness, we implemented a custom evaluation harness in `docs/eval`.

## 1. Datasets
We evaluate the pipeline on curated datasets consisting of highly cited arXiv papers across specific subdomains (e.g., NLP, Vision).
The datasets use a standard JSON schema containing:
- `dataset_name`: Name of the corpus.
- `items`: An array of paper items, each with `paper_id` and ground-truth labeled `gap_signals` for precision/recall evaluation.

## 2. Evaluation Metrics

### A) Extraction Precision
To validate the deterministic heuristic miner (Phase 3), we calculate:
- **Precision@K**: The percentage of top-K extracted gap signals that are true research gaps based on human labeling.
- **Recall@K**: The percentage of human-labeled research gaps successfully retrieved by our miner in its top K results.
- **F1 Score**: The harmonic mean of Precision and Recall.

### B) Groundedness & Hallucination Check
To validate the LLM synthesis (Phase 5), every generated "Gap Report" undergoes a groundedness validation check.
- The validator ensures that every claim in the report is appended with an `[Evidence_ID]`.
- It verifies that the cited `evidence_id` exists in the original context provided to the LLM.
- Reports that hallucinate facts or fail to properly cite the provided context are heavily penalized in the evaluation score.

## 3. Ablation Study
We run the system in three distinct configurations to prove the necessity of our pipeline components:

1. **Heuristics Only**: Generates reports using *only* the regex-extracted gap signals without any LLM synthesis. (Baseline)
2. **Heuristics + RAG**: Uses heuristic signals supplemented with semantic excerpts from ChromaDB. (Context Enhancement)
3. **Heuristics + RAG + LLM**: The full pipeline, utilizing Groq to synthesize the heuristic and vector context into a readable report. (Full System)

Results are quantified using the aforementioned metrics across these three modes.
