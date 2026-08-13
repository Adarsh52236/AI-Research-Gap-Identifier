"""Extraction pipeline service."""
import json
from pathlib import Path
from fastapi import HTTPException
from backend.app.config import settings
from backend.app.db.schemas import ExtractPaperResponse
from backend.app.core.extractor.pdf_extractor import PDFTextExtractor
from backend.app.core.extractor.text_cleaner import clean_text
from backend.app.core.extractor.section_parser import SectionParser
from backend.app.utils.file_utils import ensure_dir

class ExtractionService:
    def __init__(self):
        self.pdf_extractor = PDFTextExtractor()
        self.section_parser = SectionParser()
        
    def extract_and_process(self, local_pdf_path: Path, paper_id: str, parse_sections: bool) -> ExtractPaperResponse:
        """Runs the extraction pipeline and saves artifacts to storage."""
        if not local_pdf_path.exists():
            raise HTTPException(status_code=404, detail=f"PDF not found at {local_pdf_path}")
            
        # 1. Extract
        try:
            raw_text = self.pdf_extractor.extract_text(local_pdf_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
        # 2. Clean
        cleaned_text = clean_text(raw_text)
        
        # 3. Parse Sections
        sections = {"full_text": cleaned_text}
        sections_found = ["full_text"]
        
        if parse_sections:
            sections = self.section_parser.parse_sections(cleaned_text)
            sections_found = list(sections.keys())
            
        # 4. Save artifacts
        processed_dir = Path(settings.PROCESSED_DIR) / paper_id
        ensure_dir(processed_dir)
        
        paper_txt_path = processed_dir / "paper.txt"
        with open(paper_txt_path, "w", encoding="utf-8") as f:
            f.write(cleaned_text)
            
        sections_json_path = processed_dir / "sections.json"
        with open(sections_json_path, "w", encoding="utf-8") as f:
            json.dump(sections, f, indent=2, ensure_ascii=False)
            
        return ExtractPaperResponse(
            status="extracted",
            paper_id=paper_id,
            local_pdf_path=local_pdf_path.as_posix(),
            raw_text_path=paper_txt_path.as_posix(),
            sections_path=sections_json_path.as_posix(),
            extracted_chars=len(cleaned_text),
            sections_found=sections_found
        )
