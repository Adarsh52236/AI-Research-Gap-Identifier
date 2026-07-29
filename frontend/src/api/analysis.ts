import { apiClient } from './client';
import { AnalysisResponse } from '@/features/analysis/types';

export const analysisApi = {
  runAnalysis: (query: string, maxResults: number, signal?: AbortSignal) => {
    return apiClient<AnalysisResponse>('/analysis/run', {
      method: 'POST',
      body: JSON.stringify({ query, max_results: maxResults }),
      signal,
    });
  },
};
