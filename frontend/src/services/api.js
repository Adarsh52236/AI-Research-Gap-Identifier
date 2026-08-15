import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001',
  headers: {
    'Content-Type': 'application/json',
  },
});

import useAppStore from '../store/useAppStore';

api.interceptors.request.use((config) => {
  const token = useAppStore.getState().auth.token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    if (error.response && error.response.status === 401) {
      useAppStore.getState().logout();
      // Dispatch an event so AppShell or Landing can show the login modal if needed
      document.dispatchEvent(new CustomEvent('open-auth'));
    }
    return Promise.reject(error);
  }
);

export default api;
