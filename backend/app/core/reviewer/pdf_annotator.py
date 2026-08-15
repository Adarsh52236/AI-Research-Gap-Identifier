import pymupdf as fitz
from pathlib import Path
from backend.app.db.schemas import ReviewIssue
from backend.app.core.reviewer.pdf_locator import locate_issue
from backend.app.config import settings

def annotate_pdf(
    input_pdf_path: Path,
    output_pdf_path: Path,
    issues: list[ReviewIssue],
    overall_issues: list[str],
    overall_solutions: list[str],
) -> dict:
    
    doc = fitz.open(input_pdf_path)
    
    # Track occupied regions per page: list of fitz.Rect
    occupied_margins: dict[int, list[fitz.Rect]] = {}
    
    stats = {"issues_count": 0, "dropped_count": 0}
    
    # Define margin width based on config
    
    for issue in issues:
        loc = locate_issue(doc, issue.evidence)
        if not loc:
            stats["dropped_count"] += 1
            continue
            
        page_idx, target_rect = loc
        page = doc[page_idx]
        
        page_w = page.rect.width
        page_h = page.rect.height
        margin_w = page_w * settings.REVIEW_MARGIN_RATIO
        
        if page_idx not in occupied_margins:
            occupied_margins[page_idx] = []
            
        # Draw red rect over original text
        # Using a slight transparent fill and red border
        page.draw_rect(target_rect, color=(0.9, 0.22, 0.21), fill=(0.9, 0.22, 0.21), fill_opacity=0.1, width=1.5)
        
        # Decide margin
        target_center_x = (target_rect.x0 + target_rect.x1) / 2
        is_left = target_center_x > (page_w / 2) # if text is on right, box on left margin? The prompt:
        # "If target rect center x is left half of page -> place on right margin; else place on left margin"
        # Wait: if text is on left (x < page_w/2), put box on right margin!
        is_right_margin = target_center_x < (page_w / 2)
        
        box_width = margin_w * 0.9
        box_height = 80 # default height, could be dynamic
        
        # Find a Y position that doesn't overlap
        start_y = max(target_rect.y0 - 20, 20)
        
        # Simple collision avoidance
        placed = False
        box_rect = None
        for attempt_y in range(int(start_y), int(page_h - box_height), 10):
            if is_right_margin:
                test_rect = fitz.Rect(page_w - margin_w, attempt_y, page_w - (margin_w - box_width), attempt_y + box_height)
            else:
                test_rect = fitz.Rect(margin_w - box_width, attempt_y, margin_w, attempt_y + box_height)
                
            collision = False
            for occ in occupied_margins[page_idx]:
                if test_rect.intersects(occ):
                    collision = True
                    break
            
            if not collision:
                box_rect = test_rect
                placed = True
                break
                
        if not placed:
            stats["dropped_count"] += 1
            continue
            
        occupied_margins[page_idx].append(box_rect)
        
        # Draw box
        page.draw_rect(box_rect, color=(0.9, 0.22, 0.21), fill=(1, 1, 1), width=1)
        
        # Draw text inside box using HTML to get colored headers
        html_text = f"""
        <div style="font-family: sans-serif; font-size: 8pt; line-height: 1.2;">
            <span style="color: #E53935; font-weight: bold;">Issue:</span> {issue.issue}<br><br>
            <span style="color: #2E7D32; font-weight: bold;">Solution:</span> {issue.solution}
        </div>
        """
        text_rect = box_rect + (4, 4, -4, -4)
        page.insert_htmlbox(text_rect, html_text)
        
        # Draw arrow from box edge to target rect
        # If box is on right margin, arrow starts from left edge of box to right edge of target
        if is_right_margin:
            start_pt = fitz.Point(box_rect.x0, box_rect.y0 + 10)
            end_pt = fitz.Point(target_rect.x1, target_rect.y0 + 5)
        else:
            start_pt = fitz.Point(box_rect.x1, box_rect.y0 + 10)
            end_pt = fitz.Point(target_rect.x0, target_rect.y0 + 5)
            
        annot = page.add_line_annot(start_pt, end_pt)
        annot.set_colors(stroke=(0.9, 0.22, 0.21))
        annot.set_line_ends(fitz.PDF_ANNOT_LE_NONE, fitz.PDF_ANNOT_LE_OPEN_ARROW)
        annot.update()
        
        stats["issues_count"] += 1
        
    # Append summary page
    summary_page = doc.new_page()
    html_summary = f"""
    <div style="font-family: sans-serif; padding: 40px;">
        <h1 style="color: #333;">Reviewer Summary</h1>
        <hr>
        <h2 style="color: #E53935;">Overall Issues</h2>
        <ul>
            {''.join(f'<li>{i}</li>' for i in overall_issues)}
        </ul>
        <h2 style="color: #2E7D32;">Overall Solutions</h2>
        <ul>
            {''.join(f'<li>{s}</li>' for s in overall_solutions)}
        </ul>
    </div>
    """
    summary_page.insert_htmlbox(summary_page.rect, html_summary)
    
    doc.save(str(output_pdf_path))
    doc.close()
    
    return stats
