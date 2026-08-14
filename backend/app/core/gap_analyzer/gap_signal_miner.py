"""Gap Signal Miner."""
import hashlib
import re
from backend.app.db.schemas import GapSignal
from backend.app.core.nlp.sentence_splitter import split_sentences
from backend.app.core.nlp.gap_patterns import match_gap_patterns

def compute_alpha_ratio(text: str) -> float:
    if not text:
        return 0.0
    alpha_count = sum(1 for c in text if c.isalpha())
    return alpha_count / max(1, len(text))

def looks_like_caption_or_table(sentence: str) -> bool:
    s_lower = sentence.lower().strip()
    if s_lower.startswith(("table", "figure", "alg.", "algorithm")):
        return True
    
    # Pipes/underscores
    if sentence.count("|") > 4 or sentence.count("_") > 4:
        return True
        
    # et al. + mostly numbers
    if "et al." in s_lower:
        digits = sum(1 for c in sentence if c.isdigit())
        if digits / (len(sentence) + 1e-9) > 0.15:
            return True
            
    # Page numbers
    if re.match(r"^\s*\d+\s*$", sentence):
        return True
        
    # extremely high digit ratio
    digits = sum(1 for c in sentence if c.isdigit())
    if digits / (len(sentence) + 1e-9) > 0.35:
        return True
        
    return False

def is_noise_sentence(sentence: str) -> bool:
    if len(sentence) < 40:
        return True
    
    ar = compute_alpha_ratio(sentence)
    if ar < 0.55:
        return True
        
    if looks_like_caption_or_table(sentence):
        return True
        
    if re.search(r"([a-zA-Z])\1{19,}", sentence): # repeated chars >= 20
        return True
        
    # references heading artifacts or mostly citation markers
    s_lower = sentence.lower().strip()
    if s_lower in ["references", "bibliography"]:
        return True
        
    citation_re = re.compile(r"\[\d+(?:,\s*\d+)*\]")
    citations = citation_re.findall(sentence)
    if len(citations) >= 4 and len(sentence) < 180:
        return True
        
    return False

def quality_score(sentence: str, section: str) -> float:
    score = 1.0
    ar = compute_alpha_ratio(sentence)
    if ar < 0.65:
        score -= 0.4
        
    citation_re = re.compile(r"\[\d+(?:,\s*\d+)*\]")
    citations = citation_re.findall(sentence)
    if len(citations) >= 3:
        score -= 0.3
        
    sec_upper = section.upper()
    if sec_upper in ["FUTURE WORK", "LIMITATIONS"]:
        score += 0.3
        
    s_lower = sentence.lower()
    if any(k in s_lower for k in ["open problem", "not explored", "future work", "limitation"]):
        score += 0.1
        
    return max(0.0, min(1.0, score))


class GapSignalMiner:
    # Priority order for sections to mine
    SECTION_PRIORITY = ["FUTURE WORK", "LIMITATIONS", "CONCLUSION", "DISCUSSION", "INTRODUCTION", "full_text"]
    
    def _generate_signal_id(self, paper_id: str, sentence: str) -> str:
        """Generates a stable short id for the signal."""
        h = hashlib.sha256((paper_id + sentence).encode('utf-8')).hexdigest()
        return h[:12]

    def mine_from_sections(self, paper_id: str, sections: dict[str, str], 
                           source: str | None, year: int | None, 
                           include_sections: list[str] | None, top_k: int) -> list[GapSignal]:
        """Mines gap signals from provided sections."""
        signals = []
        
        target_sections = []
        fallback_section = None
        if include_sections:
            target_sections = [s.upper() for s in include_sections]
        else:
            for sec in self.SECTION_PRIORITY:
                if sec == "full_text":
                    fallback_section = "full_text"
                    continue
                if sec in sections or sec.upper() in sections:
                    target_sections.append(sec)
                    
        def mine_section(sec_name):
            content = sections.get(sec_name) or sections.get(sec_name.upper(), "")
            if not content: return
            for sentence in split_sentences(content):
                if is_noise_sentence(sentence):
                    continue
                hits = match_gap_patterns(sentence)
                if hits:
                    q_score = quality_score(sentence, sec_name)
                    det_score = float(len(hits))
                    if sec_name.upper() in ["FUTURE WORK", "LIMITATIONS"]:
                        det_score += 0.5
                    modal_re = re.compile(r"\b(should|could|need to|remains)\b", re.IGNORECASE)
                    if modal_re.search(sentence):
                        det_score += 0.2
                    cit_count = len(re.compile(r"\[\d+(?:,\s*\d+)*\]").findall(sentence))
                    if cit_count >= 2:
                        det_score -= 0.3
                    
                    base_score = max(0.0, det_score)
                    final_score = round(base_score * (0.6 + 0.4 * q_score), 2)
                    
                    if final_score > 0:
                        primary_pattern = hits[0][0]
                        sig = GapSignal(
                            signal_id=self._generate_signal_id(paper_id, sentence),
                            paper_id=paper_id,
                            source=source,
                            year=year,
                            section=sec_name,
                            sentence=sentence,
                            pattern=primary_pattern,
                            score=final_score,
                            quality_score=round(q_score, 2),
                            is_noise=False,
                            evidence={
                                "matched_texts": [h[1] for h in hits], 
                                "keyword_hits": [h[0] for h in hits],
                                "alpha_ratio": round(compute_alpha_ratio(sentence), 3),
                                "citation_count": cit_count
                            }
                        )
                        signals.append(sig)

        for sec in target_sections:
            mine_section(sec)
            
        if not include_sections and fallback_section and (fallback_section in sections) and len(signals) < (top_k / 3):
            mine_section(fallback_section)
            
        signals.sort(key=lambda x: (x.score, len(x.sentence)), reverse=True)
        return signals[:top_k]
