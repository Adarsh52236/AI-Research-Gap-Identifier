import os
import json
import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.chat import ChatSession, ChatMessage, ChatRole
from app.models.user import User
from app.core.config import settings
from app.services.research_analysis.service import ResearchAnalysisService

class AgentService:
    def __init__(self, db: Session, ai_service: ResearchAnalysisService):
        self.db = db
        self.ai_service = ai_service
        self.api_key = settings.groq_api_key
        self.model_name = "llama-3.3-70b-versatile"
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    def get_or_create_session(self, user: User, session_id: Optional[str] = None, initial_message: str = "") -> ChatSession:
        if session_id:
            session = self.db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == user.id).first()
            if session:
                return session
                
        # Generate title from first message
        title = initial_message[:40] + "..." if len(initial_message) > 40 else initial_message
        if not title:
            title = "New Research Chat"
            
        new_session = ChatSession(user_id=user.id, title=title)
        self.db.add(new_session)
        self.db.commit()
        self.db.refresh(new_session)
        return new_session

    def process_message(self, user: User, session_id: Optional[str], content: str) -> dict:
        """
        Process a user message, run the agent loop, and return the final response.
        """
        session = self.get_or_create_session(user, session_id, content)
        
        # Save user message
        user_msg = ChatMessage(session_id=session.id, role=ChatRole.USER, content=content)
        self.db.add(user_msg)
        self.db.commit()
        
        # Fetch history
        history = self.db.query(ChatMessage).filter(ChatMessage.session_id == session.id).order_by(ChatMessage.created_at).all()
        
        messages = [
            {"role": "system", "content": "You are ResearchOS, an expert AI Research Assistant. You help users understand complex topics, analyze research papers, and find gaps in the literature. If the user asks for a comprehensive research analysis on a topic, use the 'run_research_pipeline' tool. Otherwise, chat normally and answer their questions."}
        ]
        
        for msg in history[-10:]: # last 10 messages
            if msg.role == ChatRole.USER:
                messages.append({"role": "user", "content": msg.content})
            elif msg.role == ChatRole.ASSISTANT:
                if msg.tool_calls:
                    messages.append({"role": "assistant", "tool_calls": json.loads(msg.tool_calls)})
                else:
                    messages.append({"role": "assistant", "content": msg.content or ""})
            elif msg.role == ChatRole.TOOL:
                messages.append({"role": "tool", "content": msg.content, "tool_call_id": msg.tool_call_id})
                
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "run_research_pipeline",
                    "description": "Runs a deep research pipeline on a given query. It searches arxiv, reads papers, clusters topics, and finds research gaps.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The research topic or question"
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of papers to fetch (default 30, max 100)"
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        # Loop for agent (handle max 3 tool calls)
        for _ in range(3):
            payload = {
                "model": self.model_name,
                "messages": messages,
                "tools": tools,
                "tool_choice": "auto"
            }
            
            with httpx.Client(timeout=120) as client:
                response = client.post(self.api_url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                
            response_message = data["choices"][0]["message"]
            
            if response_message.get("tool_calls"):
                # Append assistant message with tool calls
                messages.append(response_message)
                
                # Save to DB
                asst_msg = ChatMessage(
                    session_id=session.id,
                    role=ChatRole.ASSISTANT,
                    content="",
                    tool_calls=json.dumps(response_message["tool_calls"])
                )
                self.db.add(asst_msg)
                
                # Execute tools
                for tool_call in response_message["tool_calls"]:
                    if tool_call["function"]["name"] == "run_research_pipeline":
                        args = json.loads(tool_call["function"]["arguments"])
                        query = args.get("query")
                        max_results = args.get("max_results", 30)
                        
                        try:
                            # Run actual research
                            result = self.ai_service.run_analysis(query=query, max_results=max_results)
                            
                            # Format result as markdown
                            tool_result = f"# Research Results for: {query}\n\n"
                            tool_result += f"**Overview:** Found {result.overview.papers_retrieved} papers, processed {result.overview.papers_processed}. Confidence: {result.overview.confidence*100:.0f}%\n\n"
                            
                            tool_result += "## Executive Summary\n" + result.executive_summary + "\n\n"
                            
                            tool_result += "## Key Findings\n"
                            for f in result.key_findings:
                                tool_result += f"- **{f.title} ({f.importance})**: {f.description}\n"
                                
                            tool_result += "\n## Research Gaps\n"
                            for g in result.gaps:
                                tool_result += f"- **{g.title}**: {g.description}\n"
                                
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call["id"],
                                "content": tool_result
                            })
                            
                            tool_msg = ChatMessage(
                                session_id=session.id,
                                role=ChatRole.TOOL,
                                content=tool_result,
                                tool_call_id=tool_call["id"]
                            )
                            self.db.add(tool_msg)
                            
                        except Exception as e:
                            err_str = f"Error running research pipeline: {str(e)}"
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call["id"],
                                "content": err_str
                            })
                            tool_msg = ChatMessage(
                                session_id=session.id,
                                role=ChatRole.TOOL,
                                content=err_str,
                                tool_call_id=tool_call["id"]
                            )
                            self.db.add(tool_msg)
                
                self.db.commit()
                # Continue loop to let LLM respond to tool output
            else:
                # Normal text response
                final_content = response_message.get("content", "")
                final_msg = ChatMessage(
                    session_id=session.id,
                    role=ChatRole.ASSISTANT,
                    content=final_content
                )
                self.db.add(final_msg)
                self.db.commit()
                
                return {
                    "session_id": str(session.id),
                    "message": {
                        "id": str(final_msg.id),
                        "role": "assistant",
                        "content": final_content,
                        "created_at": final_msg.created_at.isoformat()
                    }
                }
                
        raise Exception("Agent loop exceeded maximum iterations.")

