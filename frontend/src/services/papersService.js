import api from './api';

export const downloadPaper = async (pdf_url, paper_id, source, title, year) => {
  const response = await api.post('/api/v1/papers/download/', {
    pdf_url,
    paper_id,
    source,
    title,
    year,
  });
  return response.data;
};

export const extractPaper = async (local_path, paper_id, source, year) => {
  const response = await api.post('/api/v1/papers/extract/', {
    local_path,
    paper_id,
    source,
    year,
  });
  return response.data;
};
