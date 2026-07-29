from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

class AnalysisRequest(BaseModel):
    """Request payload for running a complete research analysis."""
    query: str = Field(..., min_length=1, description="The research topic to analyze.")
    max_results: int = Field(100, gt=0, le=500, description="Maximum number of papers to fetch.")

class TopicInfoSchema(BaseModel):
    id: int
    name: str
    document_count: int

class TopicModelResultSchema(BaseModel):
    topics: List[TopicInfoSchema]
    assignments: List[int]
    training_duration: float
    outlier_count: int

class EvidenceItemSchema(BaseModel):
    category: str
    message: str
    numeric_value: Optional[float] = None

class ResearchGapSchema(BaseModel):
    id: str
    title: str
    description: str
    confidence: float
    strategy: str
    supporting_topics: List[int]
    evidence: List[EvidenceItemSchema]
    created_at: datetime
    confidence_breakdown: Dict[str, float]

class GapDetectionResultSchema(BaseModel):
    total_gaps: int
    gaps: List[ResearchGapSchema]
    confidence_version: str

class ResearchInsightSchema(BaseModel):
    gap_id: str
    summary: str
    research_opportunities: List[str]
    future_directions: List[str]
    limitations: List[str]
    generated_at: datetime
    model_name: str

class AnalysisResponse(BaseModel):
    """Complete response payload for a research analysis run."""
    query: str
    papers_indexed: int
    topics: TopicModelResultSchema
    gaps: GapDetectionResultSchema
    insights: List[ResearchInsightSchema]
    started_at: datetime
    completed_at: datetime
    duration_seconds: float
