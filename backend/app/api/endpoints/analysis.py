import time
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.logging import logger
from app.api.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.services.research_analysis.service import ResearchAnalysisService
from app.services.research_analysis.exceptions import ResearchAnalysisError
from app.services.research_analysis.models import ResearchAnalysisResult

router = APIRouter()

def get_research_analysis_service() -> ResearchAnalysisService:
    """Dependency provider that wires together the entire analysis orchestration pipeline."""
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
    from app.services.llm_reasoning.provider import MockLLMProvider
    
    try:
        print("\n--- Dependency Initialization Report ---")
        
        print("Initializing PaperService...")
        paper_svc = PaperService()
        print("✓ PaperService initialized.")
        
        print("Initializing PaperPreprocessingPipeline...")
        idx_pipeline = PaperPreprocessingPipeline()
        print("✓ PaperPreprocessingPipeline initialized.")
        
        print("Initializing SentenceTransformerProvider...")
        emb_provider = SentenceTransformerProvider()
        print("✓ SentenceTransformerProvider initialized.")
        
        print("Initializing EmbeddingService...")
        emb_svc = EmbeddingService(provider=emb_provider)
        print("✓ EmbeddingService initialized.")
        
        print("Initializing ChromaVectorStore...")
        vs_store = ChromaVectorStore(collection_name="research_papers")
        print("✓ ChromaVectorStore initialized.")
        
        print("Initializing VectorStoreService...")
        vs_svc = VectorStoreService(store=vs_store)
        print("✓ VectorStoreService initialized.")
        
        print("Initializing IndexingService...")
        idx_svc = IndexingService(
            preprocessing_pipeline=idx_pipeline,
            embedding_service=emb_svc,
            vector_store_service=vs_svc
        )
        print("✓ IndexingService initialized.")
        
        print("Initializing BERTopicProvider...")
        topic_provider = BERTopicProvider()
        print("✓ BERTopicProvider initialized.")
        
        print("Initializing TopicModelingService...")
        topic_svc = TopicModelingService(provider=topic_provider)
        print("✓ TopicModelingService initialized.")
        
        print("Initializing GapDetectionService...")
        gap_strategies = [
            SparseTopicStrategy(),
            OutlierStrategy(),
            EmergingTopicStrategy(),
            TemporalGapStrategy()
        ]
        gap_svc = GapDetectionService(strategies=gap_strategies)
        print("✓ GapDetectionService initialized.")
        
        print("Initializing LLMReasoningService...")
        llm_builder = PromptBuilder()
        llm_provider = MockLLMProvider()
        llm_svc = LLMReasoningService(prompt_builder=llm_builder, provider=llm_provider)
        print("✓ LLMReasoningService initialized.")
        
        print("Initializing ResearchAnalysisService...")
        svc = ResearchAnalysisService(
            paper_service=paper_svc,
            indexing_service=idx_svc,
            topic_service=topic_svc,
            gap_service=gap_svc,
            llm_service=llm_svc
        )
        print("✓ ResearchAnalysisService initialized.")
        print("----------------------------------------\n")
        
        return svc
    except Exception as e:
        print(f"FAILED with exception: {type(e).__name__}: {e}")
        print("----------------------------------------\n")
        raise

@router.post("/analysis/run", response_model=AnalysisResponse, status_code=status.HTTP_200_OK)
def run_analysis(
    request: AnalysisRequest,
    service: ResearchAnalysisService = Depends(get_research_analysis_service)
):
    """
    Executes the complete end-to-end research analysis pipeline.
    This endpoint remains incredibly thin, delegating all coordination to the orchestration layer.
    """
    logger.info(f"API Request received: run analysis for query '{request.query}'")
    
    try:
        result: ResearchAnalysisResult = service.run_analysis(
            query=request.query,
            max_results=request.max_results
        )
        
        logger.info(f"API Request completed: {result.duration_seconds:.2f}s elapsed.")
        return result
        
    except ResearchAnalysisError as e:
        logger.warning(f"API Request failed due to logic error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error while executing research analysis API")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
