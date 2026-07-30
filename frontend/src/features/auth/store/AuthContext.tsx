import { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { User, LoginCredentials, RegisterCredentials } from '../types';
import { authClient } from '../api/authClient';
import { UNAUTHORIZED_EVENT } from '@/api/client';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isInitialized: boolean;
  isLoading: boolean;
  error: string | null;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (credentials: RegisterCredentials) => Promise<void>;
  logout: () => void;
  refreshCurrentUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('auth_token'));
  const [isInitialized, setIsInitialized] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isAuthenticated = !!token && !!user;

  const handleLogout = useCallback(() => {
    localStorage.removeItem('auth_token');
    setToken(null);
    setUser(null);
    setIsInitialized(true);
  }, []);

  const refreshCurrentUser = useCallback(async () => {
    if (!token) {
      setIsInitialized(true);
      return;
    }

    try {
      const currentUser = await authClient.getCurrentUser();
      setUser(currentUser);
    } catch (err) {
      console.error('Failed to restore session:', err);
      handleLogout();
    } finally {
      setIsInitialized(true);
    }
  }, [token, handleLogout]);

  // Initial load
  useEffect(() => {
    refreshCurrentUser();
  }, [refreshCurrentUser]);

  // Handle global 401 events
  useEffect(() => {
    const onUnauthorized = () => {
      handleLogout();
    };

    window.addEventListener(UNAUTHORIZED_EVENT, onUnauthorized);
    return () => {
      window.removeEventListener(UNAUTHORIZED_EVENT, onUnauthorized);
    };
  }, [handleLogout]);

  const login = async (credentials: LoginCredentials) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await authClient.login(credentials);
      localStorage.setItem('auth_token', response.access_token);
      setToken(response.access_token);
      
      // We manually fetch user instead of relying on effect 
      // so login resolves only when user is loaded
      const currentUser = await authClient.getCurrentUser();
      setUser(currentUser);
    } catch (err: any) {
      setError(err.message || 'Login failed');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (credentials: RegisterCredentials) => {
    setIsLoading(true);
    setError(null);
    try {
      await authClient.register(credentials);
      // Auto-login after successful registration
      await login({
        username: credentials.email,
        password: credentials.password
      });
    } catch (err: any) {
      setError(err.message || 'Registration failed');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    handleLogout();
  };

  const value = {
    user,
    token,
    isAuthenticated,
    isInitialized,
    isLoading,
    error,
    login,
    register,
    logout,
    refreshCurrentUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
