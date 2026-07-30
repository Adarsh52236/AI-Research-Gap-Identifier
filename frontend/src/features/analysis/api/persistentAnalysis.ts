import { apiClient } from '@/api/client';

export interface PersistentAnalysis {
  id: string;
  project_id: string;
  query: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  paper_count: number;
  topic_count: number;
  gap_count: number;
  summary?: string;
  raw_response?: any;
  error_message?: string;
  created_at: string;
  completed_at?: string;
}

export const persistentAnalysisApi = {
  createAnalysis: (projectId: string, query: string, maxResults: number = 100) => {
    return apiClient<PersistentAnalysis>(`/api/v1/projects/${projectId}/analyses`, {
      method: 'POST',
      params: {
        query,
        max_results: maxResults.toString(),
      },
    });
  },

  listProjectAnalyses: (projectId: string) => {
    return apiClient<PersistentAnalysis[]>(`/api/v1/projects/${projectId}/analyses`, {
      method: 'GET',
    });
  },

  getAnalysis: (analysisId: string) => {
    return apiClient<PersistentAnalysis>(`/api/v1/analyses/${analysisId}`, {
      method: 'GET',
    });
  },

  deleteAnalysis: (analysisId: string) => {
    return apiClient<void>(`/api/v1/analyses/${analysisId}`, {
      method: 'DELETE',
    });
  }
};
