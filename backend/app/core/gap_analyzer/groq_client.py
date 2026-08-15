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

    async def parse_user_prompt_json(self, query: str, user_doc_text: str | None) -> dict:
        if not self.api_key:
            raise HTTPException(status_code=500, detail="GROQ_API_KEY is missing.")
            
        system_prompt = """You are an AI research assistant. 
Your task is to parse the user's input to extract structured parameters for a research gap analysis pipeline.

RULES:
1. Return strictly JSON.
2. If the user's prompt contains a URL to a research paper (e.g., arxiv link), extract it into `extracted_url`. Otherwise, set it to null.
3. Extract core concepts, keywords, or `metrics` from the user's prompt or uploaded document.
4. Generate an `optimized_query` to be used in academic search engines (e.g., Arxiv, Semantic Scholar) to find related SOTA papers. The query must be concise and keyword-dense.

EXPECTED JSON SCHEMA:
{
  "extracted_url": "https://arxiv.org/..." | null,
  "metrics": ["keyword1", "concept2"],
  "optimized_query": "concise search query"
}"""
        
        user_prompt = f"USER QUERY:\n{query}\n\n"
        if user_doc_text:
            user_prompt += f"UPLOADED DOCUMENT EXCERPT:\n{user_doc_text[:2000]}\n"
            
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            client = AsyncGroq(api_key=self.api_key, timeout=settings.GROQ_TIMEOUT_SECONDS)
            response = await client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=messages,
                temperature=0.1,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Groq API error during preprocessing: {e}")
            # Fallback instead of failing
            return {
                "extracted_url": None,
                "metrics": [],
                "optimized_query": query
            }

