export interface User {
  id: string;
  email: string;
  full_name: string;
  username: string;
  is_active: boolean;
  is_superuser: boolean;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface LoginCredentials {
  username: string; // The backend uses OAuth2PasswordRequestForm which maps email/username to "username" field
  password: string;
}

export interface RegisterCredentials {
  email: string;
  full_name: string;
  username: string;
  password: string;
}
