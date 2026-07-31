from app.services.gap_detection.models import ResearchGap
from .exceptions import PromptGenerationError

class PromptBuilder:
    """Constructs structured prompts for LLM reasoning."""
    
    def build(self, gap: ResearchGap) -> str:
        """
        Builds a comprehensive prompt string based on the provided ResearchGap.
        """
        try:
            evidence_str = "\n".join([f"- [{e.category.upper()}] {e.message}" for e in gap.evidence])
            topics_str = ", ".join(map(str, gap.supporting_topics))
            
            prompt = f"""
You are an expert AI Research Scientist and Principal Investigator. Your task is to perform a rigorous, academic-grade analysis of a newly discovered research gap.

# Research Context
Topic/Domain: {topics_str}
Identified Gap: {gap.title}
Contextual Description: {gap.description}
Statistical Confidence: {gap.confidence:.2f} / 1.00

# Supporting Evidence Extracted from Literature
{evidence_str}

# Task Definition
Analyze the provided evidence and formulate a professional, highly analytical research gap assessment. Your analysis must be tailored specifically to the exact domain and evidence provided. Avoid generic filler.

# Required Output
Respond ONLY with a valid JSON object matching this schema exactly:
{{
  "summary": "A cohesive, highly professional paragraph (4-6 sentences) synthesizing why this specific gap exists, its academic or industrial significance, and the underlying challenges preventing its resolution thus far.",
  "research_opportunities": [
    "Specific, actionable opportunity 1 (focused on novel methodology or architecture).",
    "Specific, actionable opportunity 2 (focused on theoretical extensions)."
  ],
  "future_directions": [
    "Long-term research direction 1.",
    "Long-term research direction 2."
  ],
  "limitations": [
    "Methodological or data-related limitation to be aware of when addressing this gap.",
    "Potential confounding factors or engineering bottlenecks."
  ]
}}
"""
            return prompt.strip()
        except Exception as e:
            raise PromptGenerationError(f"Failed to generate prompt for gap {gap.id}: {e}") from e
