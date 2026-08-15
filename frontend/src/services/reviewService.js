const API_BASE_URL = 'http://localhost:8001/api/v1';

export const reviewService = {
  async annotateReview(formData) {
    const response = await fetch(`${API_BASE_URL}/review/annotate`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      let errData;
      try {
        errData = await response.json();
      } catch (e) {
        throw new Error(`Review failed with status ${response.status}`);
      }
      throw new Error(errData.detail || 'Review failed');
    }
    
    return response.json();
  },
  
  getDownloadUrl(runId) {
    return `${API_BASE_URL}/review/download/${runId}`;
  }
};
