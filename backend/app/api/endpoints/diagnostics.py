from fastapi import APIRouter, HTTPException
from app.core.logging import logger

router = APIRouter()

@router.get("/ping")
def ping():
    return {"status": "ok"}

@router.get("/database")
def test_database():
    try:
        from app.database.database import SessionLocal
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "connected"}
    except Exception as e:
        logger.exception("Diagnostic failed: Database Connection")
        raise HTTPException(status_code=500, detail="Database connection failed")

@router.get("/embedding")
def test_embedding():
    try:
        from app.services.embeddings.sentence_transformer import SentenceTransformerProvider
        provider = SentenceTransformerProvider()
        result = provider.embed("Hello World")
        return {
            "status": "success",
            "model": provider.name,
            "dimension": len(result)
        }
    except Exception as e:
        logger.exception("Diagnostic failed: Embedding Provider")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/chromadb")
def test_chromadb():
    try:
        from app.services.vectorstore.chroma_store import ChromaVectorStore
        store = ChromaVectorStore()
        return {
            "status": "connected",
            "collection_name": store.collection.name if hasattr(store, "collection") else "unknown",
            "document_count": store.count()
        }
    except Exception as e:
        logger.exception("Diagnostic failed: ChromaDB Store")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/arxiv")
def test_arxiv():
    try:
        from app.services.paper_service import PaperService
        service = PaperService()
        papers = service.search_papers(query="machine learning", max_results=3)
        return {
            "status": "success",
            "papers": [p.title for p in papers]
        }
    except Exception as e:
        logger.exception("Diagnostic failed: Arxiv PaperService")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/bertopic")
def test_bertopic():
    try:
        from app.services.topic_modeling.bertopic_provider import BERTopicProvider
        provider = BERTopicProvider()
        docs = [
            "Machine learning is great.",
            "Deep learning is a subset of machine learning.",
            "AI is transforming the world.",
            "Natural language processing is a fascinating field.",
            "Transformers have revolutionized NLP."
        ]
        result = provider.fit(docs)
        return {
            "status": "success",
            "topics": len(result.topics) if hasattr(result, "topics") else "trained"
        }
    except Exception as e:
        logger.exception("Diagnostic failed: BERTopic Provider")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/full-dependencies")
def test_full_dependencies():
    results = {}
    try:
        from app.services.paper_service import PaperService
        _ = PaperService()
        results["PaperService"] = "OK"
        
        from app.services.embeddings.sentence_transformer import SentenceTransformerProvider
        _ = SentenceTransformerProvider()
        results["SentenceTransformer"] = "OK"
        
        from app.services.embeddings.service import EmbeddingService
        _ = EmbeddingService(provider=SentenceTransformerProvider())
        results["EmbeddingService"] = "OK"
        
        from app.services.vectorstore.chroma_store import ChromaVectorStore
        _ = ChromaVectorStore()
        results["VectorStore"] = "OK"
        
        from app.services.topic_modeling.bertopic_provider import BERTopicProvider
        _ = BERTopicProvider()
        results["BERTopic"] = "OK"
        
        from app.services.gap_detection.strategies.sparse_topic import SparseTopicStrategy
        from app.services.gap_detection.service import GapDetectionService
        _ = GapDetectionService(strategies=[SparseTopicStrategy()])
        results["GapDetection"] = "OK"
        
        from app.services.llm_reasoning.prompt_builder import PromptBuilder
        from app.services.llm_reasoning.provider import MockLLMProvider
        from app.services.llm_reasoning.service import LLMReasoningService
        _ = LLMReasoningService(prompt_builder=PromptBuilder(), provider=MockLLMProvider())
        results["LLM"] = "OK"
        
        return results
    except Exception as e:
        logger.exception("Diagnostic failed: Full Dependencies Initialization")
        # Identify which dependency failed by finding the first missing key from the target list
        targets = ["PaperService", "SentenceTransformer", "EmbeddingService", "VectorStore", "BERTopic", "GapDetection", "LLM"]
        failed_service = next(iter([k for k in targets if k not in results]), "Unknown")
        results[failed_service] = f"FAILED: {type(e).__name__}"
        raise HTTPException(status_code=500, detail=results)
