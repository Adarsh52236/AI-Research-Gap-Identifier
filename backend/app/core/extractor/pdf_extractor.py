"""PDF Extraction logic."""
import fitz
from pathlib import Path
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)

class PDFTextExtractor:
    """Extracts text from PDFs using PyMuPDF."""
    
    def extract_text(self, pdf_path: Path) -> str:
        """Extract text from the given PDF path using layout-preserving blocks if possible."""
        try:
            doc = fitz.open(str(pdf_path))
            pages_text = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                blocks = page.get_text("blocks")
                
                # Each block: (x0, y0, x1, y1, text, block_type, block_no)
                # block_type 0 means text. Sort by y0 (top to bottom), then x0 (left to right)
                if blocks:
                    text_blocks = [b for b in blocks if len(b) > 4 and isinstance(b[4], str)]
                    text_blocks.sort(key=lambda b: (b[1], b[0]))
                    page_text = "\n".join([b[4].strip() for b in text_blocks])
                else:
                    # fallback
                    page_text = page.get_text("text")
                    
                pages_text.append(page_text)
                
            full_text = "\n\n--- PAGE BREAK ---\n\n".join(pages_text)
            logger.info(f"Extracted {len(doc)} pages, {len(full_text)} characters from {pdf_path.name}")
            doc.close()
            return full_text
            
        except Exception as e:
            logger.error(f"Failed to extract text from {pdf_path}: {e}")
            raise ValueError(f"Could not read PDF {pdf_path}: {e}")
