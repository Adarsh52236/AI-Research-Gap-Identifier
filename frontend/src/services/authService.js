import api from './api';

export const authService = {
  login: async (username, password) => {
    const response = await api.post('/auth/login-json', { username, password });
    return response.data;
  },

  signup: async (username, email, password) => {
    const response = await api.post('/auth/signup', { username, email, password });
    return response.data;
  },
  
  getMe: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  }
};
