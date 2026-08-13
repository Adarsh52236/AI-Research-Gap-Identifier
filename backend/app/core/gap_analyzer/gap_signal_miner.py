"""Gap Signal Miner."""
import hashlib
import re
from backend.app.db.schemas import GapSignal
from backend.app.core.nlp.sentence_splitter import split_sentences
from backend.app.core.nlp.gap_patterns import match_gap_patterns

class GapSignalMiner:
    # Priority order for sections to mine
    SECTION_PRIORITY = ["FUTURE WORK", "LIMITATIONS", "CONCLUSION", "DISCUSSION", "INTRODUCTION", "full_text"]
    
    def _generate_signal_id(self, paper_id: str, sentence: str) -> str:
        """Generates a stable short id for the signal."""
        h = hashlib.sha256((paper_id + sentence).encode('utf-8')).hexdigest()
        return h[:12]
        
    def _score_sentence(self, num_patterns: int, section: str, sentence: str) -> float:
        """Deterministically scores a sentence."""
        score = float(num_patterns)
        
        sec_upper = section.upper()
        if sec_upper in ["FUTURE WORK", "LIMITATIONS"]:
            score += 0.5
            
        modal_re = re.compile(r"\b(should|could|need to|remains)\b", re.IGNORECASE)
        if modal_re.search(sentence):
            score += 0.2
            
        # Penalty for dense citations like [12], [3]
        citation_re = re.compile(r"\[\d+(?:,\s*\d+)*\]")
        citations = citation_re.findall(sentence)
        if len(citations) >= 2:
            score -= 0.3
            
        return max(0.0, round(score, 2))

    def mine_from_sections(self, paper_id: str, sections: dict[str, str], 
                           source: str | None, year: int | None, 
                           include_sections: list[str] | None, top_k: int) -> list[GapSignal]:
        """Mines gap signals from provided sections."""
        target_sections = []
        if include_sections:
            target_sections = [s.upper() for s in include_sections]
        else:
            # Pick the best available sections in priority order
            found = False
            for sec in self.SECTION_PRIORITY:
                if sec in sections or sec.upper() in sections:
                    target_sections.append(sec)
                    found = True
            if not found and "full_text" in sections:
                target_sections.append("full_text")
                
        signals = []
        
        for sec_name in target_sections:
            # the dict keys might be upper or original case
            content = sections.get(sec_name) or sections.get(sec_name.upper(), "")
            if not content:
                continue
                
            sentences = split_sentences(content)
            for sentence in sentences:
                hits = match_gap_patterns(sentence)
                if hits:
                    score = self._score_sentence(len(hits), sec_name, sentence)
                    if score > 0:
                        # Create a signal for the primary (first) pattern hit
                        primary_pattern = hits[0][0]
                        matched_texts = [h[1] for h in hits]
                        
                        sig = GapSignal(
                            signal_id=self._generate_signal_id(paper_id, sentence),
                            paper_id=paper_id,
                            source=source,
                            year=year,
                            section=sec_name,
                            sentence=sentence,
                            pattern=primary_pattern,
                            score=score,
                            evidence={"matched_texts": matched_texts, "keyword_hits": [h[0] for h in hits]}
                        )
                        signals.append(sig)
                        
        # Sort by score desc, then by sentence length desc (tie-break)
        signals.sort(key=lambda x: (x.score, len(x.sentence)), reverse=True)
        return signals[:top_k]
