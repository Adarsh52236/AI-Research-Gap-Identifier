from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.database.database import get_db
from app.api.deps import get_current_user_dep
from app.models.user import User
from app.models.chat import ChatSession, ChatMessage
from app.services.chat.agent_service import AgentService
from app.services.research_analysis.service import ResearchAnalysisService

router = APIRouter()


def get_research_analysis_service() -> ResearchAnalysisService:
    """
    Wires together the full research analysis pipeline.
    Mirrors the factory in the old analysis.py endpoint exactly.
    """
    from app.services.paper_service import PaperService
    from app.services.preprocessing.pipeline import PaperPreprocessingPipeline
    from app.services.embeddings.service import EmbeddingService
    from app.services.embeddings.sentence_transformer import SentenceTransformerProvider
    from app.services.vectorstore.service import VectorStoreService
    from app.services.vectorstore.chroma_store import ChromaVectorStore
    from app.services.indexing.service import IndexingService
    from app.services.topic_modeling.service import TopicModelingService
    from app.services.topic_modeling.bertopic_provider import BERTopicProvider
    from app.services.gap_detection.service import GapDetectionService
    from app.services.gap_detection.strategies.sparse_topic import SparseTopicStrategy
    from app.services.gap_detection.strategies.outlier import OutlierStrategy
    from app.services.gap_detection.strategies.emerging_topic import EmergingTopicStrategy
    from app.services.gap_detection.strategies.temporal import TemporalGapStrategy
    from app.services.llm_reasoning.service import LLMReasoningService
    from app.services.llm_reasoning.prompt_builder import PromptBuilder
    from app.services.llm_reasoning.groq_provider import GroqLLMProvider
    from app.core.config import settings

    paper_svc = PaperService()
    idx_pipeline = PaperPreprocessingPipeline()
    emb_provider = SentenceTransformerProvider()
    emb_svc = EmbeddingService(provider=emb_provider)
    vs_store = ChromaVectorStore(collection_name="research_papers")
    vs_svc = VectorStoreService(store=vs_store)
    idx_svc = IndexingService(
        preprocessing_pipeline=idx_pipeline,
        embedding_service=emb_svc,
        vector_store_service=vs_svc
    )
    topic_provider = BERTopicProvider()
    topic_svc = TopicModelingService(provider=topic_provider)
    gap_strategies = [
        SparseTopicStrategy(),
        OutlierStrategy(),
        EmergingTopicStrategy(),
        TemporalGapStrategy()
    ]
    gap_svc = GapDetectionService(strategies=gap_strategies)
    llm_builder = PromptBuilder()
    llm_provider = GroqLLMProvider(
        api_key=settings.groq_api_key,
        model_name=settings.groq_model
    )
    llm_svc = LLMReasoningService(prompt_builder=llm_builder, provider=llm_provider)

    return ResearchAnalysisService(
        paper_service=paper_svc,
        indexing_service=idx_svc,
        topic_service=topic_svc,
        gap_service=gap_svc,
        llm_service=llm_svc
    )


class MessageRequest(BaseModel):
    content: str
    session_id: Optional[str] = None


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    created_at: str


class ChatResponse(BaseModel):
    session_id: str
    message: MessageResponse


class SessionSchema(BaseModel):
    id: str
    title: str
    created_at: str

    class Config:
        orm_mode = True


@router.get("/sessions", response_model=List[SessionSchema])
def list_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    sessions = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.updated_at.desc())
        .all()
    )
    return [
        {"id": str(s.id), "title": s.title, "created_at": s.created_at.isoformat()}
        for s in sessions
    ]


@router.get("/sessions/{session_id}/messages", response_model=List[MessageResponse])
def get_messages(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep)
):
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session.id)
        .order_by(ChatMessage.created_at)
        .all()
    )

    return [
        {
            "id": str(m.id),
            "role": m.role.value,
            "content": m.content,
            "created_at": m.created_at.isoformat(),
        }
        for m in messages
        if m.role.value in ["user", "assistant"]
    ]


@router.post("/message", response_model=ChatResponse)
def send_message(
    req: MessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_dep),
):
    """
    Accepts a user message and runs the agent loop.
    The AgentService decides whether to answer directly or invoke the research pipeline.
    """
    try:
        ai_service = get_research_analysis_service()
        agent = AgentService(db, ai_service)
        result = agent.process_message(current_user, req.session_id, req.content)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
