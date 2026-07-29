export interface AnalysisRequest {
  query: string;
  max_results: number;
}

export interface TopicInfo {
  id: number;
  name: string;
  document_count: number;
}

export interface TopicModelResult {
  topics: TopicInfo[];
  assignments: number[];
  training_duration: number;
  outlier_count: number;
}

export interface EvidenceItem {
  category: string;
  message: string;
  numeric_value: number | null;
}

export interface ResearchGap {
  id: string;
  title: string;
  description: string;
  confidence: number;
  strategy: string;
  supporting_topics: number[];
  evidence: EvidenceItem[];
  created_at: string;
  confidence_breakdown: Record<string, number>;
}

export interface GapDetectionResult {
  total_gaps: number;
  gaps: ResearchGap[];
  confidence_version: string;
}

export interface ResearchInsight {
  gap_id: string;
  summary: string;
  research_opportunities: string[];
  future_directions: string[];
  limitations: string[];
  generated_at: string;
  model_name: string;
}

export interface AnalysisResponse {
  query: string;
  papers_indexed: number;
  topics: TopicModelResult;
  gaps: GapDetectionResult;
  insights: ResearchInsight[];
  started_at: string;
  completed_at: string;
  duration_seconds: number;
}

export interface AnalysisError {
  type: 'network' | 'validation' | 'server' | 'timeout' | 'unknown';
  message: string;
  details?: string;
  retryable: boolean;
}

export interface AnalysisSession {
  id: string;
  timestamp: string;
  query: string;
  status: 'success' | 'error';
  data?: AnalysisResponse;
  error?: AnalysisError;
  metadata?: {
    paperCount: number;
    topicCount: number;
    gapCount: number;
    durationSeconds: number;
  };
}
