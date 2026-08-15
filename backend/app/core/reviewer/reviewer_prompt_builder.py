def build_reviewer_messages(
    extracted_text: str, 
    sectioned: dict[str, str], 
    user_prompt: str | None, 
    annotations_target: int, 
    style_guide: str | None
) -> list[dict]:
    
    style_msg = f" Ensure the feedback adheres to the {style_guide} style guide." if style_guide else ""
    user_msg = f" Additional user instruction: {user_prompt}" if user_prompt else ""
    
    system_prompt = f"""You are an expert academic peer-reviewer and critical editor. 
Your task is to identify weaknesses, methodology flaws, dataset issues, novelty gaps, or significant writing/formatting problems in the provided research paper text.

RULES:
1. You MUST output ONLY valid JSON matching the exact schema requested. No markdown blocks outside the JSON, no trailing commentary.
2. Every issue MUST be grounded in the provided text. DO NOT fabricate citations, data, baselines, or claims that are not present.
3. Identify {annotations_target} meaningful issues (fewer only if the paper is extremely short).
4. Prioritize academic/research weaknesses over minor grammar issues.
5. Each issue MUST include an `evidence` object with:
   - `anchor_phrase`: A short substring (max 80 chars) that EXACTLY matches text in the paper where the annotation should be placed.
   - `quote`: A larger contextual substring (max 240 chars) that EXACTLY matches text in the paper.
   - `page_hint`: (Optional) The 1-based page number if you can guess it, otherwise null.
6. If the `anchor_phrase` or `quote` cannot be found verbatim in the text, your annotation will be silently dropped. DO NOT hallucinate text.

JSON SCHEMA EXPECTED:
{{
  "issues": [
    {{
      "issue_id": "<unique_id>",
      "severity": "major" or "minor",
      "issue": "<short explanation of the issue>",
      "solution": "<actionable fix steps>",
      "evidence": {{
        "evidence_id": "<unique_id>",
        "page_hint": <int or null>,
        "anchor_phrase": "<exact text to highlight (max 80 chars)>",
        "quote": "<larger context (max 240 chars)>",
        "section": "<section name or null>"
      }},
      "issue_type": "<methodology|novelty|dataset|evaluation|writing|formatting>"
    }}
  ],
  "overall_issues": ["<bullet point 1>", "<bullet point 2>"],
  "overall_solutions": ["<bullet point 1>", "<bullet point 2>"]
}}
{style_msg}{user_msg}
"""

    user_content = f"Here is the extracted text of the research paper:\n\n{extracted_text}\n\n"
    user_content += "Please provide your JSON review."
    
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ]
