"""Regex patterns for mining gap signals."""
import re

# Dictionary of heuristic patterns mapping to a category name.
GAP_PATTERNS = {
    "future_work": re.compile(r"\bfuture work\b|\bfuture directions?\b|\bin future\b", re.IGNORECASE),
    "open_problem": re.compile(r"\bopen problem\b|\bremains? (an )?open\b|\bstill (an )?open\b", re.IGNORECASE),
    "not_explored": re.compile(r"\bnot (yet )?(explored|studied|addressed|investigated)\b|\bhas not been\b", re.IGNORECASE),
    "limitation": re.compile(r"\blimitation(s)?\b|\bconstraints?\b|\bshortcoming(s)?\b", re.IGNORECASE),
    "needs_improvement": re.compile(r"\bneeds? (further )?improvement\b|\bcan be improved\b|\bfurther work\b", re.IGNORECASE),
    "lack_of_data": re.compile(r"\black of\b|\binsufficient data\b|\bdata scarcity\b|\bno publicly available dataset\b", re.IGNORECASE),
    "evaluation_gap": re.compile(r"\bnot evaluated\b|\bno evaluation\b|\blimited evaluation\b|\bneeds benchmarking\b", re.IGNORECASE),
    "scalability_gap": re.compile(r"\bdoes not scale\b|\bscalability\b|\bscaling bottleneck\b", re.IGNORECASE)
}

def match_gap_patterns(sentence: str) -> list[tuple[str, str]]:
    """Returns a list of (pattern_name, matched_text) for a given sentence."""
    hits = []
    for pattern_name, pattern_regex in GAP_PATTERNS.items():
        matches = pattern_regex.findall(sentence)
        if matches:
            # Re-find first match to get exact string hit
            match_obj = pattern_regex.search(sentence)
            if match_obj:
                hits.append((pattern_name, match_obj.group(0)))
    return hits
