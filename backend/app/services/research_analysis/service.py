import time
from datetime import datetime, timezone
from typing import List

from app.core.logging import logger
from app.services.paper_service import PaperService
from app.services.indexing.service import IndexingService
from app.services.topic_modeling.service import TopicModelingService
from app.services.gap_detection.service import GapDetectionService
from app.services.llm_reasoning.service import LLMReasoningService
from app.services.llm_reasoning.models import ResearchInsight

from .models import ResearchAnalysisResult
from .exceptions import ResearchAnalysisError

class ResearchAnalysisService:
    """Orchestrates the entire end-to-end research gap identification workflow."""
    
    def __init__(
        self,
        paper_service: PaperService,
        indexing_service: IndexingService,
        topic_service: TopicModelingService,
        gap_service: GapDetectionService,
        llm_service: LLMReasoningService
    ):
        """Initializes the orchestrator with all downstream service dependencies."""
        self.paper_service = paper_service
        self.indexing_service = indexing_service
        self.topic_service = topic_service
        self.gap_service = gap_service
        self.llm_service = llm_service
        logger.info("ResearchAnalysisService initialized with all dependencies.")

    def run_analysis(self, query: str, max_results: int = 100) -> ResearchAnalysisResult:
        """
        Executes the full pipeline: search -> index -> topic model -> detect gaps -> LLM insights.
        """
        logger.info(f"Starting research analysis for query: '{query}' with max_results: {max_results}")
        
        global_start_time = time.perf_counter()
        started_at = datetime.now(timezone.utc)
        
        try:
            # 1. Search papers
            logger.info("=" * 50)
            logger.info("Stage 1/5 - Paper Retrieval")
            logger.info("=" * 50)
            stage_start = time.perf_counter()
            papers = self.paper_service.search_papers(query=query, max_results=max_results)
            logger.info(f"✓ Stage 1 completed successfully in {time.perf_counter() - stage_start:.4f}s")
            
            if not papers:
                logger.warning(f"No papers found for query '{query}'. Terminating analysis early.")
                raise ResearchAnalysisError(f"No papers found for query: {query}")
                
            # 2. Index papers
            logger.info("=" * 50)
            logger.info("Stage 2/5 - Paper Indexing")
            logger.info("=" * 50)
            stage_start = time.perf_counter()
            indexing_result = self.indexing_service.index_papers(papers)
            logger.info(f"✓ Stage 2 completed successfully in {time.perf_counter() - stage_start:.4f}s")
            
            documents = [f"{p.title}\n{p.abstract}" for p in papers]

            # 3. Train topic model
            logger.info("=" * 50)
            logger.info("Stage 3/5 - Topic Modeling")
            logger.info("=" * 50)
            stage_start = time.perf_counter()
            topic_result = self.topic_service.train(documents)
            logger.info(f"✓ Stage 3 completed successfully in {time.perf_counter() - stage_start:.4f}s")
            
            # 4. Detect research gaps
            logger.info("=" * 50)
            logger.info("Stage 4/5 - Gap Detection")
            logger.info("=" * 50)
            stage_start = time.perf_counter()
            gap_result = self.gap_service.detect_gaps(topic_result)
            logger.info(f"✓ Stage 4 completed successfully in {time.perf_counter() - stage_start:.4f}s")
            
            # 5. Generate LLM insights
            logger.info("=" * 50)
            logger.info("Stage 5/5 - LLM Insight Generation")
            logger.info("=" * 50)
            stage_start = time.perf_counter()
            insights: List[ResearchInsight] = []
            
            for gap in gap_result.gaps:
                try:
                    insight = self.llm_service.generate_insight(gap)
                    insights.append(insight)
                except Exception as e:
                    # Fault tolerance: log and continue processing remaining gaps
                    logger.exception(f"Failed to generate LLM insight for gap '{gap.id}' ({gap.title}): {e}")
                    
            logger.info(f"✓ Stage 5 completed successfully in {time.perf_counter() - stage_start:.4f}s")
            
            global_duration = time.perf_counter() - global_start_time
            completed_at = datetime.now(timezone.utc)
            
            logger.info("=" * 50)
            logger.info("Research Analysis Completed Successfully")
            logger.info("=" * 50)
            logger.info(f"Query: {query}")
            logger.info(f"Papers Retrieved: {len(papers)}")
            logger.info(f"Papers Indexed: {indexing_result.indexed_papers}")
            logger.info(f"Topics Generated: {len(topic_result.topics)}")
            logger.info(f"Gaps Detected: {gap_result.total_gaps}")
            logger.info(f"Insights Generated: {len(insights)}")
            logger.info(f"Total Runtime: {global_duration:.4f}s")
            
            return ResearchAnalysisResult(
                query=query,
                papers_indexed=indexing_result.indexed_papers,
                topics=topic_result,
                gaps=gap_result,
                insights=insights,
                started_at=started_at,
                completed_at=completed_at,
                duration_seconds=global_duration
            )
            
        except ResearchAnalysisError:
            raise
        except Exception as e:
            logger.info("=" * 50)
            logger.info("Pipeline Failed")
            logger.info("=" * 50)
            logger.info(f"Exception Type: {type(e).__name__}")
            logger.info(f"Exception Message: {str(e)}")
            logger.exception("Research analysis pipeline failed unexpectedly")
            raise ResearchAnalysisError(f"Pipeline failed: {e}") from e
