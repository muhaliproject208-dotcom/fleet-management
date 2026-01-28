import { getFriendlyErrorMessage } from '../utils/errorMessages';

const API_URL = process.env.NEXT_PUBLIC_API_URL!;

export interface ApiResponse<T = unknown> {
  data?: T | null;
  error?: string;
  message?: string;
  fieldErrors?: Record<string, string>;
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
      // Extract error message from various response formats
      let errorMessage = data.error || data.message || data.detail || 'An error occurred';
      
      // Handle DRF validation errors (object with field keys)
      const fieldErrors: Record<string, string> = {};
      if (typeof data === 'object' && !data.error && !data.message && !data.detail) {
        const fields = Object.keys(data);
        if (fields.length > 0) {
          // This is likely a field validation error object
          for (const field of fields) {
            const fieldError = data[field];
            if (Array.isArray(fieldError) && fieldError.length > 0) {
              fieldErrors[field] = getFriendlyErrorMessage(fieldError[0]);
            } else if (typeof fieldError === 'string') {
              fieldErrors[field] = getFriendlyErrorMessage(fieldError);
            }
          }
          // Use first field error as main error message
          errorMessage = Object.values(fieldErrors)[0] || errorMessage;
        }
      }
      
      return {
        error: getFriendlyErrorMessage(errorMessage),
        fieldErrors: Object.keys(fieldErrors).length > 0 ? fieldErrors : undefined,
        data: null,
      };
    }

    return { data, message: data.message };
  } catch (error) {
    return {
      error: getFriendlyErrorMessage(error instanceof Error ? error.message : 'Network error'),
      data: null,
    };
  }
}

export { API_URL };
