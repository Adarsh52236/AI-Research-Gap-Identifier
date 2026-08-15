import api from './api';

export const authService = {
  login: async (username, password) => {
    const response = await api.post('/api/v1/auth/login-json', { username, password });
    return response.data;
  },

  signup: async (username, email, password) => {
    const response = await api.post('/api/v1/auth/signup', { username, email, password });
    return response.data;
  },
  
  getMe: async () => {
    const response = await api.get('/api/v1/auth/me');
    return response.data;
  }
};
