import api from './api';

export const runsService = {
  startPipelineRun: async (payload) => {
    const response = await api.post('/analysis/pipeline-run/', payload, {
      params: { async_run: true }
    });
    return response.data;
  },
  
  getRunStatus: async (runId) => {
    const response = await api.get(`/analysis/pipeline-run/${runId}`);
    return response.data;
  },
  
  getRunReport: async (runId) => {
    const response = await api.get(`/analysis/pipeline-run/${runId}/report`);
    return response.data;
  },
  
  listRuns: async () => {
    try {
      const response = await api.get('/analysis/runs');
      return response.data;
    } catch (error) {
      if (error.response && error.response.status === 404) {
        return []; // graceful fallback
      }
      throw error;
    }
  },
  
  deleteRun: async (runId) => {
    const response = await api.delete(`/analysis/runs/${runId}`);
    return response.data;
  },
  
  clearAllRuns: async () => {
    const response = await api.delete('/analysis/runs');
    return response.data;
  }
};
