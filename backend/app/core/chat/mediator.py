import json
from groq import AsyncGroq
from backend.app.config import settings
from backend.app.utils.logger import get_logger

logger = get_logger(__name__)

class ChatMediator:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        if not self.api_key:
            logger.error("GROQ_API_KEY is not set.")

    async def mediate(self, chat_history: list[dict], new_query: str) -> dict:
        """
        Takes the previous chat history and the new user query.
        Returns a dict indicating whether to reply as chat or trigger analysis.
        """
        if not self.api_key:
            # Fallback if no API key
            return {"type": "analysis", "topic": new_query}

        system_prompt = """You are an AI research assistant and mediator.
Your primary role is to help researchers find and analyze research papers to identify research gaps.
You are having a conversation with the user.
If the user says hello, asks how you are, or asks general questions, reply conversationally and helpfully.
If the user asks you to analyze a topic, find research gaps, or research a specific domain, you MUST call the `start_research_analysis` tool.

Do NOT call the tool if the user is just chatting.
ONLY call the tool when the user makes a clear request for literature review, gap analysis, or paper research."""

        messages = [{"role": "system", "content": system_prompt}]
        for msg in chat_history:
            # Only include user/assistant roles
            if msg.get("role") in ["user", "assistant"]:
                messages.append({"role": msg["role"], "content": msg["content"]})
        
        messages.append({"role": "user", "content": new_query})

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "start_research_analysis",
                    "description": "Trigger a heavy backend research gap analysis pipeline on a specific topic. Use this tool ONLY when the user explicitly asks to analyze papers, find gaps, or research a topic.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "topic": {
                                "type": "string",
                                "description": "The research topic or query to analyze."
                            }
                        },
                        "required": ["topic"]
                    }
                }
            }
        ]

        try:
            client = AsyncGroq(api_key=self.api_key, timeout=settings.GROQ_TIMEOUT_SECONDS)
            response = await client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=messages,
                temperature=0.3,
                tools=tools,
                tool_choice="auto",
                max_tokens=1024
            )
            
            message = response.choices[0].message
            
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    if tool_call.function.name == "start_research_analysis":
                        args = json.loads(tool_call.function.arguments)
                        return {
                            "type": "analysis",
                            "topic": args.get("topic", new_query)
                        }
            
            # If no tool was called, return the text response
            return {
                "type": "chat",
                "content": message.content or "I'm not sure how to respond to that."
            }
            
        except Exception as e:
            logger.error(f"Groq API error during mediation: {e}")
            # Fallback to analysis if LLM fails, as it's the core feature
            return {"type": "analysis", "topic": new_query}
