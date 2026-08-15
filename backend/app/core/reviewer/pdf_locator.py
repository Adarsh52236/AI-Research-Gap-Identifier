import pymupdf as fitz
from backend.app.db.schemas import ReviewEvidence
from backend.app.config import settings

def find_best_rect_for_anchor(page: fitz.Page, anchor_phrase: str) -> fitz.Rect | None:
    # 1. Direct search
    rects = page.search_for(anchor_phrase)
    if rects:
        # If multiple, just pick the first one (or we could pick largest)
        # return an inflated rect to nicely encompass the text
        return rects[0] + (-2, -2, 2, 2)
    
    # 2. Try shortened substring (first 40 chars)
    shortened = anchor_phrase[:40]
    if len(shortened) > 10:
        rects = page.search_for(shortened)
        if rects:
            return rects[0] + (-2, -2, 2, 2)
            
    return None

def locate_issue(doc: fitz.Document, evidence: ReviewEvidence) -> tuple[int, fitz.Rect] | None:
    # If page hint exists (1-based), try it first
    if evidence.page_hint and 1 <= evidence.page_hint <= len(doc):
        page_idx = evidence.page_hint - 1
        page = doc[page_idx]
        rect = find_best_rect_for_anchor(page, evidence.anchor_phrase)
        if rect:
            return page_idx, rect
            
    # Otherwise, scan pages up to configured limit
    limit = min(settings.REVIEW_MAX_PAGES_SCAN, len(doc))
    for i in range(limit):
        if evidence.page_hint and (i == evidence.page_hint - 1):
            continue # already checked
            
        page = doc[i]
        rect = find_best_rect_for_anchor(page, evidence.anchor_phrase)
        if rect:
            return i, rect
            
    return None
