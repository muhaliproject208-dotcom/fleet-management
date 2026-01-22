const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export interface ApiResponse<T = unknown> {
  data?: T | null;
  error?: string;
  message?: string;
}

export async function apiRequest<T = unknown>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  try {
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
    
    const headers = new Headers(options.headers);
    if (!headers.has('Content-Type')) {
      headers.set('Content-Type', 'application/json');
    }

    if (token && !endpoint.includes('/register') && !endpoint.includes('/login')) {
      headers.set('Authorization', `Bearer ${token}`);
    }

    const response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers,
    });

    const data = await response.json();

    if (!response.ok) {
      return {
        error: data.error || data.message || 'An error occurred',
        data: null,
      };
    }

    return { data, message: data.message };
  } catch (error) {
    return {
      error: error instanceof Error ? error.message : 'Network error',
      data: null,
    };
  }
}

export { API_URL };
