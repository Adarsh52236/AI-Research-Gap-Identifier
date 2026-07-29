from app.services.gap_detection.models import ResearchGap
from .exceptions import PromptGenerationError

class PromptBuilder:
    """Constructs structured prompts for LLM reasoning."""
    
    def build(self, gap: ResearchGap) -> str:
        """
        Builds a comprehensive prompt string based on the provided ResearchGap.
        """
        try:
            evidence_str = "\n".join([f"- {e.category}: {e.message}" for e in gap.evidence])
            topics_str = ", ".join(map(str, gap.supporting_topics))
            
            prompt = f"""
You are an expert AI research assistant. Analyze the following discovered research gap and provide structured insights.

# Discovered Gap
Title: {gap.title}
Description: {gap.description}
Confidence Score: {gap.confidence:.2f}
Supporting Topics: {topics_str}

# Evidence
{evidence_str}

# Instructions
Based strictly on the provided information, please:
1. Explain why this may represent a significant research gap.
2. Suggest concrete future research directions.
3. Mention any potential limitations or caveats.
4. Avoid unsupported claims or hallucinating external information.

Please return the output in JSON format with the following keys:
- "summary" (string)
- "research_opportunities" (list of strings)
- "future_directions" (list of strings)
- "limitations" (list of strings)
"""
            return prompt.strip()
        except Exception as e:
            raise PromptGenerationError(f"Failed to generate prompt for gap {gap.id}: {e}") from e
