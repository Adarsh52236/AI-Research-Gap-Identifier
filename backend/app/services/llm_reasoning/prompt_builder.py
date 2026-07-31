import json

class PromptBuilder:
    """Constructs structured prompts for LLM synthesis engine."""
    
    def build_topic_refinement(self, raw_name: str, paper_abstracts: list[str]) -> str:
        """Phase 1: Generates a prompt to refine a raw topic into human-readable data."""
        abstracts_str = "\n---\n".join(paper_abstracts)
        
        return f"""
You are an expert AI Research Scientist. Your task is to analyze a raw thematic cluster of academic papers and give it a professional, human-readable name, description, and keywords.

# Raw Topic Information
Internal ID/Name: {raw_name}

# Representative Abstracts
{abstracts_str}

# Task
Based on the representative abstracts, generate a cohesive topic name, a 2-sentence description, and 3-5 keywords.

# Required Output
Respond ONLY with a valid JSON object matching this schema exactly:
{{
  "name": "A clear, professional title for this research theme (e.g., 'Multimodal Learning Architectures')",
  "description": "A 2-sentence summary of what this topic encompasses.",
  "keywords": ["keyword1", "keyword2", "keyword3"]
}}
"""

    def build_gap_refinement(self, gap_title: str, gap_desc: str, topics: list[str], abstracts: list[str]) -> str:
        """Phase 2: Generates a prompt to refine a detected gap."""
        abstracts_str = "\n---\n".join(abstracts)
        topics_str = ", ".join(topics)
        
        return f"""
You are an expert AI Research Scientist. We have algorithmically detected a potential research gap in the literature. Your task is to validate and articulate this gap professionally.

# Context
Related Topics: {topics_str}
Initial Gap Title: {gap_title}
Initial Signal Description: {gap_desc}

# Representative Literature
{abstracts_str}

# Task
Formulate a rigorous, academic-grade research gap. Explain why it exists (reasoning) and propose future directions to solve it.

# Required Output
Respond ONLY with a valid JSON object matching this schema exactly:
{{
  "title": "A highly professional, specific title for this research gap.",
  "description": "A 2-3 sentence description of the gap.",
  "reasoning": "A 2-3 sentence explanation of WHY this gap exists and why it hasn't been solved.",
  "future_directions": ["Actionable research direction 1", "Actionable research direction 2"]
}}
"""

    def build_executive_summary(self, query: str, topics: list[str], gaps: list[str]) -> str:
        """Phase 3: Generates the global executive summary and key findings."""
        topics_str = "\n".join([f"- {t}" for t in topics])
        gaps_str = "\n".join([f"- {g}" for g in gaps])
        
        return f"""
You are the Lead Research Analyst for ResearchOS. Synthesize the findings of an automated literature review into an Executive Summary.

# Research Context
Original Query: "{query}"

# Discovered Topics
{topics_str}

# Major Research Gaps Identified
{gaps_str}

# Task
1. Write a 3-4 paragraph Executive Summary explaining the overall research landscape, dominant themes, limitations, and future opportunities. It must read as a cohesive narrative.
2. Extract 3 to 6 "Key Findings" that stand out from the analysis.

# Required Output
Respond ONLY with a valid JSON object matching this schema exactly:
{{
  "text": "The full 3-4 paragraph executive summary.",
  "key_findings": [
    {{
      "title": "Short title of finding",
      "description": "1-2 sentence description",
      "importance": "High/Medium"
    }}
  ]
}}
"""
