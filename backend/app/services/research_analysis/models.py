from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from datetime import datetime

@dataclass
class OverviewResult:
    papers_retrieved: int
    papers_processed: int
    year_range: str
    processing_duration: float
    confidence: float
    timestamp: datetime

@dataclass
class KeyFindingResult:
    title: str
    description: str
    supporting_evidence: int
    importance: str

@dataclass
class TopicResult:
    id: int
    name: str
    description: str
    keywords: List[str]
    document_count: int
    representative_papers: List[str]

@dataclass
class ResearchGapResult:
    id: str
    title: str
    description: str
    reasoning: str
    confidence: float
    future_directions: List[str]
    supporting_papers: List[str]

@dataclass
class EvidenceResult:
    id: int
    title: str
    authors: str
    year: int
    abstract: str
    pdf_url: Optional[str]
    topic_assignment: int

@dataclass
class TrendsResult:
    publication_timeline: Dict[str, int]
    top_keywords: List[str]
    top_authors: List[str]
    top_institutions: List[str]

@dataclass
class GraphNodeResult:
    id: str
    label: str
    type: str
    size: int

@dataclass
class GraphEdgeResult:
    source: str
    target: str
    weight: int

@dataclass
class KnowledgeGraphResult:
    nodes: List[GraphNodeResult]
    edges: List[GraphEdgeResult]

@dataclass
class ResearchAnalysisResult:
    """Represents the complete output of an end-to-end research analysis run."""
    query: str
    overview: OverviewResult
    executive_summary: str
    key_findings: List[KeyFindingResult]
    topics: List[TopicResult]
    gaps: List[ResearchGapResult]
    evidence: List[EvidenceResult]
    trends: TrendsResult
    knowledge_graph: KnowledgeGraphResult
