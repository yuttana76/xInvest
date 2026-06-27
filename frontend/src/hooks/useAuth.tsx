'use client';

import { useState, useEffect, createContext, useContext, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import { 
  UserProfile, 
  setTokens, 
  getAccessToken, 
  getRefreshToken,
  getUserFromToken, 
  clearTokens,
  authApi 
} from '@/lib/auth';
import { jwtDecode } from 'jwt-decode';

interface AuthContextType {
  user: UserProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<{ otp_ref: string }>;
  verifyOTP: (username: string, otp_code: string) => Promise<UserProfile>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const initAuth = () => {
      const token = getAccessToken();
      const refresh = getRefreshToken();
      
      if (token && refresh) {
        try {
          const decodedRefresh = jwtDecode<{ exp: number }>(refresh);
          const currentTime = Date.now() / 1000;
          
          if (decodedRefresh.exp < currentTime) {
            // refresh token is expired
            clearTokens();
            setUser(null);
            setIsLoading(false);
            return;
          }
        } catch {
          clearTokens();
          setUser(null);
          setIsLoading(false);
          return;
        }

        const profile = getUserFromToken(token);
        if (profile && profile.role) {
          setUser(profile);
        } else {
          clearTokens();
        }
      } else {
        clearTokens();
      }
      setIsLoading(false);
    };
    initAuth();
  }, []);

  const login = async (username: string, password: string) => {
    try {
      const response = await authApi.post('/api/v1/auth/login/', { username, password });
      return response.data;
    } catch (error: unknown) {
      if (axios.isAxiosError(error)) {
        throw error.response?.data?.error || 'Login failed';
      }
      throw 'Login failed';
    }
  };

  const verifyOTP = async (username: string, otp_code: string) => {
    try {
      const response = await authApi.post('/api/v1/auth/verify-otp/', { username, otp_code });
      const { access, refresh, role, email } = response.data;
      
      setTokens(access, refresh);
      const profile: UserProfile = { username, email, role };
      setUser(profile);
      
      console.log('*Role:', role);
      console.log('*Profile:', profile);

      const hasRole = (r: string) => {
        if (Array.isArray(role)) {
          return role.map(x => x.toUpperCase()).includes(r.toUpperCase());
        }
        return role.toUpperCase() === r.toUpperCase();
      };

      if (hasRole('admin') || hasRole('IT')) {
        router.push('/admin-portal');
      } else if (hasRole('operator') || hasRole('cp-risk') || hasRole('officer')) {
        router.push('/operator');
      } else if (hasRole('marketing') || hasRole('ceo')) {
        router.push('/marketing');
      } else if (hasRole('agent')) {
        router.push('/agent');
      } else if (hasRole('investor')) {
        router.push('/dashboard-inv');
      } else {
        router.push('/');
      }
      
      return profile;
    } catch (error: unknown) {
      if (axios.isAxiosError(error)) {
        throw error.response?.data?.error || 'OTP verification failed';
      }
      throw 'OTP verification failed';
    }
  };

  const logout = () => {
    clearTokens();
    setUser(null);
    window.location.href = '/';
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, isLoading, login, verifyOTP, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
