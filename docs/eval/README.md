# Evaluation Harness

This directory contains templates and documentation for evaluating the AI Research Gap Identifier.

## Creating a Dataset
1. Copy `dataset_template.json` to a new file (e.g. `datasets/eval_v1.json`).
2. Populate it with papers that have been processed through the pipeline (ensure `sections.json` and `gap_signals.json` exist in `storage/processed/`).

## Labeling
1. Copy `labels_template.json` to a new file (e.g. `labels/eval_v1_labels.json`).
2. Have human annotators fill in the ground truth:
   - **Signal evaluation**: Find `signal_id`s in the paper's `gap_signals.json` and mark `is_true_gap_statement`.
   - **Report evaluation**: Mark `is_grounded` and `is_useful` for the generated LLM reports.

## Running Evaluations
- Run signal evaluation: `PYTHONPATH=. python backend/scripts/eval_gap_signals.py`
- Run report groundedness: `PYTHONPATH=. python backend/scripts/eval_gap_reports.py`
- Run ablation studies: `PYTHONPATH=. python backend/scripts/ablation_runner.py`
