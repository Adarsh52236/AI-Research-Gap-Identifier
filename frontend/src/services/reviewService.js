import api from './api';

export const reviewService = {
  async annotateReview(formData) {
    try {
      const response = await api.post('/review/annotate/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      if (error.response && error.response.data && error.response.data.detail) {
        throw new Error(error.response.data.detail);
      }
      throw new Error(error.message || 'Review failed');
    }
  },
  
  getDownloadUrl(runId) {
    return `${api.defaults.baseURL}/review/download/${runId}`;
  }
};
