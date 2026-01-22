import { apiRequest, ApiResponse } from './index';

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  phone_number?: string;
  role: 'superuser' | 'fleet_manager' | 'transport_supervisor';
  email_verified: boolean;
  is_active: boolean;
}

export interface RegisterData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  phone_number?: string;
  role: 'fleet_manager' | 'transport_supervisor';
}

export interface LoginData {
  email: string;
  password: string;
}

export interface LoginResponse {
  message: string;
  user: User;
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_at: string;
}

export interface RegisterResponse {
  message: string;
  user: User;
  email_verification_required: boolean;
  otp_sent: boolean;
}

// Register new user
export async function register(data: RegisterData): Promise<ApiResponse<RegisterResponse>> {
  return apiRequest<RegisterResponse>('/auth/register/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

// Verify OTP
export async function verifyOTP(email: string, token: string): Promise<ApiResponse> {
  return apiRequest('/auth/verify-otp/', {
    method: 'POST',
    body: JSON.stringify({ email, token }),
  });
}

// Resend OTP
export async function resendOTP(email: string, type: 'signup' | 'recovery' = 'signup'): Promise<ApiResponse> {
  return apiRequest('/auth/resend-otp/', {
    method: 'POST',
    body: JSON.stringify({ email, type }),
  });
}

// Login
export async function login(data: LoginData): Promise<ApiResponse<LoginResponse>> {
  const response = await apiRequest<LoginResponse>('/auth/login/', {
    method: 'POST',
    body: JSON.stringify(data),
  });

  // Save tokens to localStorage
  if (response.data && typeof window !== 'undefined') {
    localStorage.setItem('access_token', response.data.access_token);
    localStorage.setItem('refresh_token', response.data.refresh_token);
    localStorage.setItem('user', JSON.stringify(response.data.user));
  }

  return response;
}

// Logout
export async function logout(): Promise<ApiResponse> {
  const response = await apiRequest('/auth/logout/', {
    method: 'POST',
  });

  // Clear localStorage
  if (typeof window !== 'undefined') {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  }

  return response;
}

// Get user profile
export async function getProfile(): Promise<ApiResponse<User>> {
  return apiRequest<User>('/auth/profile/');
}

// Update user profile
export async function updateProfile(data: Partial<User>): Promise<ApiResponse<User>> {
  return apiRequest<User>('/auth/profile/', {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

// Password reset request
export async function requestPasswordReset(email: string): Promise<ApiResponse> {
  return apiRequest('/auth/password-reset/', {
    method: 'POST',
    body: JSON.stringify({ email }),
  });
}

// Verify password reset OTP
export async function verifyPasswordResetOTP(email: string, token: string): Promise<ApiResponse<{ access_token: string }>> {
  return apiRequest('/auth/password-reset/verify-otp/', {
    method: 'POST',
    body: JSON.stringify({ email, token }),
  });
}

// Confirm password reset
export async function confirmPasswordReset(access_token: string, new_password: string): Promise<ApiResponse> {
  return apiRequest('/auth/password-reset/confirm/', {
    method: 'POST',
    body: JSON.stringify({ access_token, new_password }),
  });
}

// Refresh token
export async function refreshToken(): Promise<ApiResponse<{ access_token: string; refresh_token: string }>> {
  const refresh = typeof window !== 'undefined' ? localStorage.getItem('refresh_token') : null;
  
  if (!refresh) {
    return { error: 'No refresh token available' };
  }

  const response = await apiRequest<{ access_token: string; refresh_token: string }>('/auth/token/refresh/', {
    method: 'POST',
    body: JSON.stringify({ refresh_token: refresh }),
  });

  // Update tokens
  if (response.data && typeof window !== 'undefined') {
    localStorage.setItem('access_token', response.data.access_token);
    if (response.data.refresh_token) {
      localStorage.setItem('refresh_token', response.data.refresh_token);
    }
  }

  return response;
}

// Get current user from localStorage
export function getCurrentUser(): User | null {
  if (typeof window === 'undefined') return null;
  const user = localStorage.getItem('user');
  return user ? JSON.parse(user) : null;
}

// Check if user is authenticated
export function isAuthenticated(): boolean {
  if (typeof window === 'undefined') return false;
  return !!localStorage.getItem('access_token');
}
