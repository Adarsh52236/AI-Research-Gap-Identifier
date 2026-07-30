import { apiClient } from '@/api/client';
import { User, AuthResponse, LoginCredentials, RegisterCredentials } from '../types';

export const authClient = {
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    // Backend uses OAuth2PasswordRequestForm which requires form-urlencoded data
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'}/api/v1/auth/login`, {
      method: 'POST',
      body: formData,
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      throw new Error(data.detail || data.message || `API Error: ${response.status}`);
    }

    return data as AuthResponse;
  },

  register: async (credentials: RegisterCredentials): Promise<User> => {
    return apiClient<User>('/api/v1/auth/register', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  },

  getCurrentUser: async (): Promise<User> => {
    return apiClient<User>('/api/v1/auth/me', {
      method: 'GET',
    });
  },
};
