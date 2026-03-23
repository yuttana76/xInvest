import axios from 'axios';
import { jwtDecode } from 'jwt-decode';

const API_URL = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/api$/, '');

export const authApi = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface UserProfile {
  username: string;
  email: string;
  role: 'admin' | 'investor' | 'operator' | 'marketing' | 'agent' | 'guest';
}

export const setTokens = (access: string, refresh: string) => {
  localStorage.setItem('access_token', access);
  localStorage.setItem('refresh_token', refresh);
};

export const getAccessToken = () => localStorage.getItem('access_token');
export const getRefreshToken = () => localStorage.getItem('refresh_token');

export const clearTokens = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
};

export const getUserFromToken = (token: string): UserProfile | null => {
  try {
    const decoded = jwtDecode<UserProfile & { exp: number }>(token);
    return {
      username: decoded.username,
      email: decoded.email,
      role: decoded.role,
    };
  } catch {
    return null;
  }
};

// Request Interceptor to add Access Token
authApi.interceptors.request.use(
  (config) => {
    const token = getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor for Token Refresh
authApi.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = getRefreshToken();
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_URL}/api/v1/auth/token-refresh/`, {
            refresh: refreshToken,
          });
          const { access } = response.data;
          setTokens(access, refreshToken);
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return authApi(originalRequest);
        } catch {
          clearTokens();
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

export const requestPasswordReset = async (username: string, email: string) => {
  try {
    const response = await authApi.post('/api/v1/auth/password-reset/', { username, email });
    return response.data;
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      throw error.response?.data?.error || error.response?.data?.message || 'Failed to request password reset';
    }
    throw 'An unexpected error occurred';
  }
};

export const confirmPasswordReset = async (uidb64: string, token: string, new_password: string) => {
  try {
    const response = await authApi.post('/api/v1/auth/password-reset-confirm/', {
      uidb64,
      token,
      new_password,
    });
    return response.data;
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      throw error.response?.data?.error || error.response?.data?.message || 'Failed to reset password';
    }
    throw 'An unexpected error occurred';
  }
};
