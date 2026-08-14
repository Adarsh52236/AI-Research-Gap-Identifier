"""Prompt builder for Gap Report."""
from backend.app.db.schemas import EvidenceItem

def build_gap_report_messages(query: str | None, evidence: list[EvidenceItem], user_document_text: str | None = None) -> list[dict]:
    
    system_prompt = """You are an expert AI research scientist tasked with identifying high-value research gaps.
You will be provided with a set of evidence excerpts from research papers.
You will ALSO be provided with the user's research document (if available).
Your job is to synthesize these excerpts into a structured JSON research gap report.

RULES:
1. You MUST output ONLY valid JSON matching the exact schema requested.
2. Every claim or gap you propose MUST be grounded in the provided evidence.
3. If a user document is provided, you MUST compare it against the evidence. Identify specific gaps, missing methodologies, or limitations in the user's document relative to the SOTA evidence.
4. If an explicit fact is not in the evidence, do not state it. Do not hallucinate capabilities or limitations.
5. Each gap must include a list of `citations`. These citations MUST exactly match the `evidence_id` keys provided. DO NOT cite paper titles or names, only use the `evidence_id` string.
6. If you cannot find any gaps in the evidence, return an empty gaps list with notes explaining why.

SCHEMA EXPECTED:
{
  "status": "ok",
  "query": <query string or null>,
  "created_at": <iso timestamp>,
  "model": <model name>,
  "paper_ids": [<list of paper ids>],
  "gaps": [
    {
      "gap_id": "<unique short id>",
      "title": "<short descriptive title>",
      "summary": "<summary of the gap>",
      "why_it_is_a_gap": "<evidence-based reasoning>",
      "proposed_research_questions": ["<rq1>", "<rq2>"],
      "suggested_methodology": ["<step1>"],
      "suggested_evaluation": ["<eval1>"],
      "risks_and_limitations": ["<risk1>"],
      "citations": ["<evidence_id_1>", "<evidence_id_2>"],
      "confidence": <float between 0 and 1>
    }
  ],
  "notes": "<optional constraints/notes>"
}
"""

    evidence_text = "EVIDENCE ITEMS:\n\n"
    for e in evidence:
        evidence_text += f"--- EVIDENCE ID: {e.evidence_id} ---\n"
        evidence_text += f"Paper ID: {e.paper_id}\n"
        if e.section:
            evidence_text += f"Section: {e.section}\n"
        evidence_text += f"Text: {e.text}\n\n"
        
    user_prompt = f"Analyze the following evidence and generate a research gap report.\n"
    if query:
        user_prompt += f"Focus particularly on this domain/query: {query}\n\n"
        
    if user_document_text:
        user_prompt += f"USER'S RESEARCH DOCUMENT:\n{user_document_text}\n\n"
        
    user_prompt += evidence_text
    
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
