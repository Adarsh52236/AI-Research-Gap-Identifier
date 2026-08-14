import sys
import json
import time
from pathlib import Path

def run_mode_a():
    """Mode A: Heuristics only. No vector embeddings, no LLM."""
    print("Running MODE A: Heuristics only...")
    # Mocking execution for script demo
    output = "# Ablation Mode A: Heuristics Only\n\nGap Signals ranked purely by rule-based scoring."
    save_output("mode_a", output)

def run_mode_b():
    """Mode B: Heuristics + Vector Excerpts. No LLM reasoning."""
    print("Running MODE B: Heuristics + Vectors...")
    output = "# Ablation Mode B: Heuristics + Vectors\n\nGap Signals clustered using semantic similarity."
    save_output("mode_b", output)

def run_mode_c():
    """Mode C: Full Pipeline. Heuristics + Vectors + LLM."""
    print("Running MODE C: Full Pipeline...")
    output = "# Ablation Mode C: Full Pipeline\n\nFull LLM reasoning applied on top of vector-retrieved evidence."
    save_output("mode_c", output)

def save_output(mode: str, content: str):
    ts = int(time.time())
    out_dir = Path("storage/reports/ablation")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{ts}_{mode}.md"
    
    with open(out_path, "w") as f:
        f.write(content)
        
    print(f"[{mode.upper()}] Output saved to: {out_path}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python backend/scripts/ablation_runner.py <mode>\nModes: A, B, C, ALL")
        sys.exit(1)
        
    mode = sys.argv[1].upper()
    
    if mode in ["A", "ALL"]:
        run_mode_a()
    if mode in ["B", "ALL"]:
        run_mode_b()
    if mode in ["C", "ALL"]:
        run_mode_c()
        
    if mode not in ["A", "B", "C", "ALL"]:
        print("Invalid mode. Choose A, B, C, or ALL.")

if __name__ == "__main__":
    main()
