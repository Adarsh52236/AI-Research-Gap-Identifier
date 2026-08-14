import api from './api';

export const mineGapSignals = async (paper_ids) => {
  const response = await api.post('/api/v1/analysis/gap-signals/', {
    paper_ids,
  });
  return response.data;
};

export const indexEmbeddings = async (paper_ids) => {
  const response = await api.post('/api/v1/analysis/index-embeddings/', {
    paper_ids,
  });
  return response.data;
};

export const generateGapReport = async (paper_ids, query) => {
  const response = await api.post('/api/v1/analysis/gap-report/', {
    paper_ids,
    query,
  });
  return response.data;
};
