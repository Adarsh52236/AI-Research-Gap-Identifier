const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

interface FetchOptions extends RequestInit {
  params?: Record<string, string>;
}

export async function apiClient<T>(endpoint: string, options: FetchOptions = {}): Promise<T> {
  const { params, headers, ...customConfig } = options;
  
  const url = new URL(endpoint, BASE_URL);
  if (params) {
    Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));
  }

  const config: RequestInit = {
    ...customConfig,
    headers: {
      'Content-Type': 'application/json',
      ...headers,
    },
  };

  try {
    const response = await fetch(url.toString(), config);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || data.message || `API Error: ${response.status}`);
    }

    return data as T;
  } catch (error: any) {
    if (error.name === 'AbortError') {
      throw new Error('Request cancelled');
    }
    throw error;
  }
}
