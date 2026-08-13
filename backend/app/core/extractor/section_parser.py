"""Parses academic paper sections based on heuristics."""
import re

class SectionParser:
    """Parser to split raw academic paper text into distinct sections."""
    
    # Common academic headings (case-insensitive for regex later)
    # We allow optional numbering like "1. ", "1 ", "IV. "
    HEADING_PATTERNS = [
        "ABSTRACT", "INTRODUCTION", "RELATED WORK", "PRIOR WORK", "BACKGROUND",
        "METHODOLOGY", "METHODS", "METHOD", "EXPERIMENTS", "EVALUATION", 
        "RESULTS", "DISCUSSION", "CONCLUSION", "CONCLUSIONS", "FUTURE WORK", 
        "LIMITATIONS", "REFERENCES", "BIBLIOGRAPHY", "ACKNOWLEDGMENTS"
    ]
    
    def parse_sections(self, text: str) -> dict[str, str]:
        """Splits full_text into dict of sections."""
        sections = {"full_text": text}
        if not text:
            return sections
            
        # Build regex for headings. E.g. ^(\d+\.?\s*|[IVXLCDM]+\.?\s*)?(ABSTRACT|INTRODUCTION|...)\s*$
        headings_re = "|".join([re.escape(h) for h in self.HEADING_PATTERNS])
        pattern = re.compile(
            rf"^(?:\d+(?:\.\d+)*\.?\s*|[IVXLCDM]+\.?\s*)?({headings_re})(?:\s*\n|$)", 
            re.IGNORECASE | re.MULTILINE
        )
        
        matches = list(pattern.finditer(text))
        
        if not matches:
            # If no matches, fallback to inferring abstract
            sections.update(self._infer_abstract_fallback(text))
            return sections
            
        # Extract sections between matches
        for i, match in enumerate(matches):
            sec_name = match.group(1).upper()
            start_idx = match.end()
            end_idx = matches[i+1].start() if i + 1 < len(matches) else len(text)
            
            content = text[start_idx:end_idx].strip()
            # If the section already exists, append to it (e.g. multiple RESULTS subheaders)
            if sec_name in sections:
                sections[sec_name] += "\n\n" + content
            else:
                sections[sec_name] = content
                
        # If no Abstract was explicitly found, try to infer it.
        if "ABSTRACT" not in sections:
            inferred = self._infer_abstract_fallback(text)
            if "ABSTRACT" in inferred:
                sections["ABSTRACT"] = inferred["ABSTRACT"]
                
        return sections
        
    def _infer_abstract_fallback(self, text: str) -> dict[str, str]:
        """Tries to guess where the abstract is if 'ABSTRACT' heading is missing."""
        intro_match = re.search(r"^(?:\d+\.?\s*|[IVXLCDM]+\.?\s*)?INTRODUCTION(?:\s*\n|$)", text, re.IGNORECASE | re.MULTILINE)
        if intro_match:
            # Everything before INTRODUCTION (up to 1500 chars) might contain the abstract
            pre_intro = text[:intro_match.start()].strip()
            # Grab the last 1500 chars before intro as a guess for the abstract
            # to avoid grabbing author lists/affiliations which can be noisy.
            abstract_guess = pre_intro[-1500:].strip()
            if abstract_guess:
                return {"ABSTRACT": abstract_guess}
        return {}
