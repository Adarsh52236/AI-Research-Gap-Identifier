import api from './api';

export const authService = {
  login: async (username, password) => {
    // FastAPI OAuth2 requires form data
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    const response = await api.post('/api/v1/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });
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
