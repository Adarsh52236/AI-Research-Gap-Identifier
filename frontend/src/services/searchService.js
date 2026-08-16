import api from './api';

export const searchPapers = async (query, limit = 10, sources = ['arxiv', 'semantic_scholar']) => {
  const response = await api.post('/search/', {
    query,
    limit,
    sources,
  });
  return response.data;
};
