import time
import json
from datetime import datetime, timezone
from app.core.logging import logger
from app.services.gap_detection.models import ResearchGap
from .base import LLMProvider
from .prompt_builder import PromptBuilder
from .models import ResearchInsight
from .exceptions import LLMReasoningError, LLMProviderError

class LLMReasoningService:
    """Orchestrates LLM prompt building and insight generation via dependency injection."""
    
    def __init__(self, prompt_builder: PromptBuilder, provider: LLMProvider):
        """Initializes the service with prompt building logic and a target provider."""
        self.prompt_builder = prompt_builder
        self.provider = provider
        logger.info(f"LLMReasoningService initialized with provider: {self.provider.name}")
        
    def generate_insight(self, gap: ResearchGap) -> ResearchInsight:
        """Generates structured reasoning insights for a given research gap."""
        logger.info(f"Generating insight for gap ID: {gap.id}")
        start_time = time.perf_counter()
        
        try:
            # 1. Prompt Generation
            prompt = self.prompt_builder.build(gap)
            logger.info("Prompt generated successfully.")
            
            # 2. Provider Execution
            logger.info(f"Executing LLM provider ({self.provider.name})...")
            raw_response = self.provider.generate(prompt)
            
            # Parse the JSON response
            try:
                parsed_response = json.loads(raw_response)
            except json.JSONDecodeError:
                logger.warning("LLM response was not valid JSON. Falling back to raw text mappings.")
                parsed_response = {
                    "summary": raw_response,
                    "research_opportunities": [],
                    "future_directions": [],
                    "limitations": []
                }
            
            insight = ResearchInsight(
                gap_id=gap.id,
                summary=parsed_response.get("summary", "No summary provided."),
                research_opportunities=parsed_response.get("research_opportunities", []),
                future_directions=parsed_response.get("future_directions", []),
                limitations=parsed_response.get("limitations", []),
                generated_at=datetime.now(timezone.utc),
                model_name=self.provider.name
            )
            
            duration = time.perf_counter() - start_time
            logger.info(f"LLM insight generation completed in {duration:.4f}s for gap ID: {gap.id}")
            
            return insight
            
        except Exception as e:
            logger.error(f"Failed to generate insight for gap ID: {gap.id}. Error: {e}")
            raise LLMReasoningError(f"Failed to generate insight: {e}") from e
