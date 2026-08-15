import uuid
import logging
from pathlib import Path
from backend.app.config import settings
from backend.app.db.schemas import ReviewAnnotateRequest, ReviewAnnotateResponse
from backend.app.core.extractor.extraction_service import ExtractionService
from backend.app.core.reviewer.reviewer_llm_client import ReviewerLLMClient
from backend.app.core.reviewer.reviewer_prompt_builder import build_reviewer_messages
from backend.app.core.reviewer.evidence_validator import validate_and_filter_issues
from backend.app.core.reviewer.pdf_annotator import annotate_pdf

logger = logging.getLogger(__name__)

class ReviewService:
    def __init__(self):
        self.extractor = ExtractionService()
        self.llm_client = ReviewerLLMClient()

    async def generate_annotated_review(
        self, input_pdf_path: Path, request: ReviewAnnotateRequest, run_id: str | None = None
    ) -> ReviewAnnotateResponse:
        
        run_id = run_id or str(uuid.uuid4())
        
        # 1. Extract text
        ext_res = self.extractor.extract_and_process(
            local_pdf_path=input_pdf_path,
            paper_id=run_id,
            parse_sections=False
        )
        
        with open(ext_res.raw_text_path, "r", encoding="utf-8") as f:
            raw_text = f.read()
            
        # 2. Call LLM
        messages = build_reviewer_messages(
            extracted_text=raw_text,
            sectioned={},
            user_prompt=request.prompt,
            annotations_target=request.annotations_target,
            style_guide=request.style_guide
        )
        llm_output = await self.llm_client.generate_review_json(messages)
        
        # 3. Validate evidence
        valid_output, dropped = validate_and_filter_issues(llm_output, raw_text)
        
        notes = None
        if len(valid_output.issues) < settings.REVIEW_MIN_ISSUES:
            notes = "Note: Fewer issues than requested were found. This could be due to a short paper, lack of identifiable issues, or OCR limitations in the uploaded PDF."
            
        # 4. Annotate PDF
        output_dir = Path(settings.REVIEW_REPORTS_DIR) / run_id
        output_dir.mkdir(parents=True, exist_ok=True)
        out_pdf_path = output_dir / "Research_Paper_Annotated_Issues_Solutions.pdf"
        
        stats = annotate_pdf(
            input_pdf_path=input_pdf_path,
            output_pdf_path=out_pdf_path,
            issues=valid_output.issues,
            overall_issues=valid_output.overall_issues,
            overall_solutions=valid_output.overall_solutions
        )
        
        return ReviewAnnotateResponse(
            status="ok",
            review_run_id=run_id,
            input_pdf_path=str(input_pdf_path),
            annotated_pdf_path=str(out_pdf_path),
            issues_count=stats["issues_count"],
            dropped_count=dropped + stats["dropped_count"],
            notes=notes
        )
