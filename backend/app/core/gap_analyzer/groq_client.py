"""Groq LLM Client."""
import json
import asyncio
from fastapi import HTTPException
from groq import AsyncGroq
from backend.app.config import settings
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)

class GroqLLMClient:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        if not self.api_key:
            logger.error("GROQ_API_KEY is not set.")
            
    async def generate_gap_report_json(self, messages: list[dict]) -> str:
        if not self.api_key:
            raise HTTPException(status_code=500, detail="GROQ_API_KEY is missing.")
            
        try:
            client = AsyncGroq(api_key=self.api_key, timeout=settings.GROQ_TIMEOUT_SECONDS)
            response = await client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=messages,
                temperature=settings.GROQ_TEMPERATURE,
                max_tokens=settings.GROQ_MAX_TOKENS,
                response_format={"type": "json_object"}
            )
            
            return response.choices[0].message.content
        except asyncio.TimeoutError:
            raise HTTPException(status_code=504, detail="Groq API timeout.")
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise HTTPException(status_code=502, detail=f"Upstream AI Error: {str(e)}")
