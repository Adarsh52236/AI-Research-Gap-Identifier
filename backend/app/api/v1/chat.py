import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.db.session import get_db
from backend.app.db.models import ChatSession, ChatMessage, User
from backend.app.core.deps import get_current_user
from pydantic import BaseModel

router = APIRouter()

# Pydantic models for request/response
class ChatMessageBase(BaseModel):
    role: str
    content: str
    run_id: Optional[str] = None

class ChatMessageResponse(ChatMessageBase):
    id: str
    session_id: str
    created_at: datetime
    
    class Config:
        orm_mode = True

class ChatSessionBase(BaseModel):
    title: str

class ChatSessionResponse(ChatSessionBase):
    id: str
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ChatSessionWithMessagesResponse(ChatSessionResponse):
    messages: List[ChatMessageResponse]

@router.get("/sessions", response_model=List[ChatSessionResponse])
def get_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sessions = db.query(ChatSession).filter(ChatSession.user_id == current_user.id).order_by(desc(ChatSession.updated_at)).all()
    return sessions

@router.post("/sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(
    session_data: ChatSessionBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session_id = str(uuid.uuid4())
    new_session = ChatSession(
        id=session_id,
        user_id=current_user.id,
        title=session_data.title
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

@router.put("/sessions/{session_id}", response_model=ChatSessionResponse)
def update_session(
    session_id: str,
    session_data: ChatSessionBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.title = session_data.title
    session.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(session)
    return session

@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    db.delete(session)
    db.commit()
    return None

@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
def get_messages(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify session belongs to user
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at).all()
    return messages

@router.post("/sessions/{session_id}/messages", response_model=ChatMessageResponse, status_code=status.HTTP_201_CREATED)
def create_message(
    session_id: str,
    message_data: ChatMessageBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    msg_id = str(uuid.uuid4())
    new_msg = ChatMessage(
        id=msg_id,
        session_id=session_id,
        role=message_data.role,
        content=message_data.content,
        run_id=message_data.run_id
    )
    db.add(new_msg)
    
    session.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(new_msg)
    return new_msg

class ChatOrchestrateRequest(BaseModel):
    query: str
    limit: int = 5
    sources: List[str] = ["arxiv", "semantic_scholar"]
    user_document_text: Optional[str] = None
    steps: List[str] = ["search", "download", "extract", "mine", "index", "report"]

@router.post("/sessions/{session_id}/orchestrate")
async def orchestrate_chat(
    session_id: str,
    request: ChatOrchestrateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Verify session
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # 2. Save user message
    user_msg_id = str(uuid.uuid4())
    user_msg = ChatMessage(
        id=user_msg_id,
        session_id=session_id,
        role="user",
        content=request.query
    )
    db.add(user_msg)
    db.commit()

    # 3. Fetch history
    history_records = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at).all()
    history = [{"role": m.role, "content": m.content} for m in history_records[:-1]] # exclude the one we just added for context if we pass new_query separately

    # 4. Invoke Mediator
    from backend.app.core.chat.mediator import ChatMediator
    mediator = ChatMediator()
    
    # Append document text for the LLM to see
    mediator_query = request.query
    if request.user_document_text:
        mediator_query += f"\n\n[USER ATTACHED DOCUMENT EXTRACT]:\n{request.user_document_text[:2000]}"
        
    decision = await mediator.mediate(history, mediator_query)

    if decision["type"] == "chat":
        # Save assistant text reply
        ast_msg_id = str(uuid.uuid4())
        ast_msg = ChatMessage(
            id=ast_msg_id,
            session_id=session_id,
            role="assistant",
            content=decision["content"]
        )
        db.add(ast_msg)
        session.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(ast_msg)
        
        return {
            "type": "chat",
            "message": {
                "id": ast_msg.id,
                "session_id": ast_msg.session_id,
                "role": ast_msg.role,
                "content": ast_msg.content,
                "run_id": ast_msg.run_id,
                "created_at": ast_msg.created_at.isoformat()
            }
        }
    
    elif decision["type"] == "analysis":
        # Trigger pipeline run
        from backend.app.core.pipeline.pipeline_runner import PipelineRunner
        from backend.app.core.pipeline.run_store import get_run_store
        from backend.app.db.schemas import PipelineRunRequest, PipelineRunStatus
        import asyncio

        run_id = str(uuid.uuid4())
        topic = decision.get("topic", request.query)
        
        store = get_run_store()
        initial_status = PipelineRunStatus(
            run_id=run_id,
            session_id=session_id,
            user_id=current_user.id,
            status="pending",
            steps=request.steps,
            query=topic,
            started_at=datetime.utcnow().isoformat()
        )
        store.create_run(initial_status)

        run_request = PipelineRunRequest(
            run_id=run_id,
            session_id=session_id,
            query=topic,
            limit=request.limit,
            sources=request.sources,
            user_document_text=request.user_document_text,
            steps=request.steps
        )

        runner = PipelineRunner()
        # Ensure we run async runner safely
        asyncio.create_task(runner.run(run_request, user_id=current_user.id))

        return {
            "type": "analysis",
            "run_id": run_id,
            "topic": topic
        }
