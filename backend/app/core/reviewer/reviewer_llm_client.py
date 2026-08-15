import json
import logging
from groq import AsyncGroq
from backend.app.config import settings
from backend.app.db.schemas import ReviewLLMOutput

logger = logging.getLogger(__name__)

class ReviewerLLMClient:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        if not self.api_key:
            logger.error("GROQ_API_KEY is not set.")

    async def generate_review_json(self, messages: list[dict]) -> ReviewLLMOutput:
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is missing.")
            
        try:
            client = AsyncGroq(api_key=self.api_key)
            response = await client.chat.completions.create(
                messages=messages,
                model=settings.GROQ_MODEL,
                temperature=settings.GROQ_TEMPERATURE,
                max_tokens=2048, # increased limit for detailed reviews
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from Groq")
            
            parsed = json.loads(content)
            return ReviewLLMOutput(**parsed)
            
        except Exception as e:
            logger.error(f"Failed to generate review from Groq: {e}", exc_info=True)
            raise
