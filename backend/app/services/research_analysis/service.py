import time
from collections import Counter
from datetime import datetime, timezone
from typing import List, Dict, Any

from app.core.logging import logger
from app.services.paper_service import PaperService
from app.services.indexing.service import IndexingService
from app.services.topic_modeling.service import TopicModelingService
from app.services.gap_detection.service import GapDetectionService
from app.services.llm_reasoning.service import LLMReasoningService

from .models import (
    ResearchAnalysisResult, OverviewResult, KeyFindingResult, 
    TopicResult, ResearchGapResult, EvidenceResult, TrendsResult, 
    KnowledgeGraphResult, GraphNodeResult, GraphEdgeResult
)
from .exceptions import ResearchAnalysisError

class ResearchAnalysisService:
    """Orchestrates the entire end-to-end research analysis workflow."""
    
    def __init__(
        self,
        paper_service: PaperService,
        indexing_service: IndexingService,
        topic_service: TopicModelingService,
        gap_service: GapDetectionService,
        llm_service: LLMReasoningService
    ):
        self.paper_service = paper_service
        self.indexing_service = indexing_service
        self.topic_service = topic_service
        self.gap_service = gap_service
        self.llm_service = llm_service
        logger.info("ResearchAnalysisService initialized with Synthesis Engine.")

    def run_analysis(self, query: str, max_results: int = 100) -> ResearchAnalysisResult:
        logger.info(f"Starting research analysis for query: '{query}' with max_results: {max_results}")
        
        global_start_time = time.perf_counter()
        started_at = datetime.now(timezone.utc)
        
        try:
            # 1. Search papers
            logger.info("Stage 1 - Paper Retrieval")
            papers = self.paper_service.search_papers(query=query, max_results=max_results)
            if not papers:
                raise ResearchAnalysisError(f"No papers found for query: {query}")
                
            # 2. Index papers
            logger.info("Stage 2 - Paper Indexing")
            indexing_result = self.indexing_service.index_papers(papers)
            documents = [f"{p.title}\n{p.abstract}" for p in papers]

            # 3. Train topic model
            logger.info("Stage 3 - Topic Modeling")
            topic_result = self.topic_service.train(documents)
            
            # 4. Detect research gaps
            logger.info("Stage 4 - Gap Detection")
            gap_result = self.gap_service.detect_gaps(topic_result)
            
            # 5. LLM Synthesis Phase 1: Topic Refinement
            logger.info("Stage 5 - LLM Phase 1 (Topic Refinement)")
            refined_topics: List[TopicResult] = []
            topic_name_map = {}
            for t in topic_result.topics:
                # Find representative papers for this topic
                rep_indices = [i for i, assignment in enumerate(topic_result.assignments) if assignment == t.id][:5]
                rep_abstracts = [papers[i].abstract for i in rep_indices if i < len(papers)]
                rep_titles = [papers[i].title for i in rep_indices if i < len(papers)]
                
                # Default to generic name for outlier topic (-1)
                if t.id == -1:
                    refined = TopicResult(
                        id=-1, name="General Literature", description="Uncategorized papers.", 
                        keywords=["general"], document_count=t.document_count, representative_papers=rep_titles
                    )
                else:
                    llm_topic = self.llm_service.refine_topic(t.name, rep_abstracts)
                    refined = TopicResult(
                        id=t.id, name=llm_topic.name, description=llm_topic.description,
                        keywords=llm_topic.keywords, document_count=t.document_count,
                        representative_papers=rep_titles
                    )
                refined_topics.append(refined)
                topic_name_map[t.id] = refined.name

            # 6. LLM Synthesis Phase 2: Gap Refinement
            logger.info("Stage 6 - LLM Phase 2 (Gap Refinement)")
            refined_gaps: List[ResearchGapResult] = []
            for g in gap_result.gaps:
                # Get abstracts for supporting topics
                supporting_abstracts = []
                for tid in g.supporting_topics:
                    indices = [i for i, assign in enumerate(topic_result.assignments) if assign == tid][:2]
                    supporting_abstracts.extend([papers[i].abstract for i in indices if i < len(papers)])
                
                related_topic_names = [topic_name_map.get(tid, str(tid)) for tid in g.supporting_topics]
                
                llm_gap = self.llm_service.refine_gap(g.id, g.title, g.description, related_topic_names, supporting_abstracts[:5])
                
                # Get titles of supporting papers
                supporting_indices = []
                for tid in g.supporting_topics:
                    supporting_indices.extend([i for i, assign in enumerate(topic_result.assignments) if assign == tid])
                supporting_papers_titles = [papers[i].title for i in supporting_indices[:5] if i < len(papers)]

                refined_gaps.append(ResearchGapResult(
                    id=llm_gap.gap_id, title=llm_gap.title, description=llm_gap.description,
                    reasoning=llm_gap.reasoning, confidence=g.confidence,
                    future_directions=llm_gap.future_directions, supporting_papers=supporting_papers_titles
                ))

            # 7. LLM Synthesis Phase 3: Executive Summary
            logger.info("Stage 7 - LLM Phase 3 (Executive Summary)")
            topic_names = [rt.name for rt in refined_topics if rt.id != -1]
            gap_titles = [rg.title for rg in refined_gaps]
            exec_summary = self.llm_service.generate_executive_summary(query, topic_names, gap_titles)
            
            key_findings = [KeyFindingResult(
                title=kf.title, description=kf.description, importance=kf.importance,
                supporting_evidence=len(papers) // 10 + 1 # Mock calculation
            ) for kf in exec_summary.key_findings]

            # 8. Data Aggregation: Evidence, Trends, Knowledge Graph
            logger.info("Stage 8 - Data Aggregation")
            evidence: List[EvidenceResult] = []
            years = []
            authors = []
            for i, p in enumerate(papers):
                topic_id = topic_result.assignments[i] if i < len(topic_result.assignments) else -1
                evidence.append(EvidenceResult(
                    id=i, title=p.title, authors=", ".join(p.authors),
                    year=p.published_date.year if p.published_date else 2024,
                    abstract=p.abstract, pdf_url=p.pdf_url, topic_assignment=topic_id
                ))
                if p.published_date:
                    years.append(p.published_date.year)
                authors.extend(p.authors)
                
            year_range = f"{min(years)}-{max(years)}" if years else "Unknown"
            timeline = dict(Counter(years))
            top_authors = [a for a, c in Counter(authors).most_common(5)]
            all_keywords = []
            for rt in refined_topics:
                all_keywords.extend(rt.keywords)
            top_keywords = [k for k, c in Counter(all_keywords).most_common(10)]

            trends = TrendsResult(
                publication_timeline={str(k): v for k, v in timeline.items()},
                top_keywords=top_keywords,
                top_authors=top_authors,
                top_institutions=["Stanford University", "MIT", "Google DeepMind"] # Mock
            )

            nodes = []
            for rt in refined_topics:
                if rt.id != -1:
                    nodes.append(GraphNodeResult(id=str(rt.id), label=rt.name, type="topic", size=rt.document_count))
            edges = [] # Could algorithmically generate edges based on co-occurrence
            kg = KnowledgeGraphResult(nodes=nodes, edges=edges)

            global_duration = time.perf_counter() - global_start_time
            
            overview = OverviewResult(
                papers_retrieved=len(papers), papers_processed=indexing_result.indexed_papers,
                year_range=year_range, processing_duration=global_duration,
                confidence=gap_result.gaps[0].confidence if gap_result.gaps else 0.85,
                timestamp=datetime.now(timezone.utc)
            )

            logger.info("Research Analysis Completed Successfully")
            
            return ResearchAnalysisResult(
                query=query, overview=overview, executive_summary=exec_summary.text,
                key_findings=key_findings, topics=refined_topics, gaps=refined_gaps,
                evidence=evidence, trends=trends, knowledge_graph=kg
            )
            
        except Exception as e:
            logger.exception("Research analysis pipeline failed unexpectedly")
            raise ResearchAnalysisError(f"Pipeline failed: {e}") from e
