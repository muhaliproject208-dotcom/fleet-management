const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export interface ApiResponse<T = unknown> {
  data?: T | null;
  error?: string;
  message?: string;
}

let isRefreshing = false;
let refreshPromise: Promise<boolean> | null = null;

async function attemptTokenRefresh(): Promise<boolean> {
  if (typeof window === 'undefined') return false;
  
  const refreshToken = localStorage.getItem('refresh_token');
  if (!refreshToken) return false;

  try {
    const response = await fetch(`${API_URL}/auth/token/refresh/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (response.ok) {
      const data = await response.json();
      localStorage.setItem('access_token', data.access_token);
      if (data.refresh_token) {
        localStorage.setItem('refresh_token', data.refresh_token);
      }
      return true;
    }
  } catch (error) {
    console.error('Token refresh failed:', error);
  }
  
  return false;
}

export async function apiRequest<T = unknown>(
  endpoint: string,
  options: RequestInit = {},
  retryOnAuth = true
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

    // Handle 401 - Unauthorized (expired or invalid token)
    if (response.status === 401 && retryOnAuth && !endpoint.includes('/auth/token/refresh/')) {
      // If already refreshing, wait for the existing refresh to complete
      if (isRefreshing && refreshPromise) {
        const refreshed = await refreshPromise;
        if (refreshed) {
          return apiRequest<T>(endpoint, options, false);
        }
      } else {
        // Start new refresh
        isRefreshing = true;
        refreshPromise = attemptTokenRefresh();
        const refreshed = await refreshPromise;
        isRefreshing = false;
        refreshPromise = null;

        if (refreshed) {
          // Retry the original request with new token
          return apiRequest<T>(endpoint, options, false);
        }
      }
      
      // Token refresh failed, clear auth data and indicate auth error
      if (typeof window !== 'undefined') {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        
        // Redirect to login if we're on the client
        if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
          window.location.href = '/login';
        }
      }
      
      return {
        error: 'Authentication expired. Please login again.',
        data: null,
      };
    }

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
