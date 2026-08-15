import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.app.core.reviewer.review_service import ReviewService
from backend.app.db.schemas import ReviewAnnotateRequest

async def main():
    if len(sys.argv) < 2:
        print("Usage: python manual_review_annotate_test.py <path_to_pdf>")
        return
        
    pdf_path = Path(sys.argv[1])
    if not pdf_path.exists():
        print(f"Error: {pdf_path} does not exist.")
        return
        
    service = ReviewService()
    req = ReviewAnnotateRequest(
        prompt="Focus on methodology and statistical soundness.",
        annotations_target=5
    )
    
    print(f"Starting review for {pdf_path}...")
    res = await service.generate_annotated_review(pdf_path, req)
    
    print(f"Review completed successfully.")
    print(f"Issues generated: {res.issues_count}")
    print(f"Issues dropped (hallucinated/unlocatable): {res.dropped_count}")
    print(f"Annotated PDF saved to: {res.annotated_pdf_path}")
    if res.notes:
        print(f"Notes: {res.notes}")

if __name__ == "__main__":
    asyncio.run(main())
