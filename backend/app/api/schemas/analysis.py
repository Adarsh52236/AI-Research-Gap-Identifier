from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime

class AnalysisRequest(BaseModel):
    """Request payload for running a complete research analysis."""
    query: str = Field(..., min_length=1, description="The research topic to analyze.")
    max_results: int = Field(100, gt=0, le=500, description="Maximum number of papers to fetch.")

# SECTION 1: Overview
class OverviewSchema(BaseModel):
    papers_retrieved: int
    papers_processed: int
    year_range: str
    processing_duration: float
    confidence: float
    timestamp: datetime

# SECTION 3: Key Findings
class KeyFindingSchema(BaseModel):
    title: str
    description: str
    supporting_evidence: int
    importance: str

# SECTION 4: Research Topics
class TopicSchema(BaseModel):
    id: int
    name: str
    description: str
    keywords: List[str]
    document_count: int
    representative_papers: List[str]

# SECTION 5: Gap Detection
class ResearchGapSchema(BaseModel):
    id: str
    title: str
    description: str
    reasoning: str
    confidence: float
    future_directions: List[str]
    supporting_papers: List[str]

# SECTION 6: Evidence Explorer
class EvidenceSchema(BaseModel):
    id: int
    title: str
    authors: str
    year: int
    abstract: str
    pdf_url: Optional[str]
    topic_assignment: int

# SECTION 7: Research Trends
class TrendsSchema(BaseModel):
    publication_timeline: Dict[str, int]
    top_keywords: List[str]
    top_authors: List[str]
    top_institutions: List[str]

# SECTION 8: Knowledge Graph
class GraphNode(BaseModel):
    id: str
    label: str
    type: str
    size: int

class GraphEdge(BaseModel):
    source: str
    target: str
    weight: int

class KnowledgeGraphSchema(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]

# FULL RESPONSE
class AnalysisResponse(BaseModel):
    """Complete response payload tailored for the frontend redesign."""
    query: str
    overview: OverviewSchema
    executive_summary: str
    key_findings: List[KeyFindingSchema]
    topics: List[TopicSchema]
    gaps: List[ResearchGapSchema]
    evidence: List[EvidenceSchema]
    trends: TrendsSchema
    knowledge_graph: KnowledgeGraphSchema
