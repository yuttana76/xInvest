'use client';

import React, { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/Button';
import { Input } from '@/components/Input';
import { Lock, User, ArrowRight, ShieldCheck } from 'lucide-react';
import axios from 'axios';

export default function LoginPage() {
  const { login, verifyOTP } = useAuth();
  const [step, setStep] = useState(1); // 1: Login, 2: OTP
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [otpCode, setOtpCode] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [otpRef, setOtpRef] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    try {
      const data = await login(username, password);
      setOtpRef(data.otp_ref);
      setStep(2);
    } catch (err: unknown) {
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.error || 'Login failed');
      } else if (typeof err === 'string') {
        setError(err);
      } else {
        setError('Login failed');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerifyOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    try {
      await verifyOTP(username, otpCode);
    } catch (err: unknown) {
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.error || 'Verification failed');
      } else if (typeof err === 'string') {
        setError(err);
      } else {
        setError('Verification failed');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 relative overflow-hidden bg-slate-50 dark:bg-slate-950 transition-colors duration-300 text-slate-900 dark:text-white">
      {/* Background Decor */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary/20 dark:bg-primary/10 blur-[120px] rounded-full -z-10" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-accent/20 dark:bg-accent/10 blur-[120px] rounded-full -z-10" />

      <div className="w-full max-w-md">
        <div className="text-center mb-10">
          <div className="inline-flex items-center gap-2 mb-6">
            <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center shadow-lg shadow-primary/20">
              <span className="text-white font-bold text-xl text-center">x</span>
            </div>
            <span className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">Invest</span>
          </div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">
            {step === 1 ? 'Welcome Back' : 'Security Verification'}
          </h1>
          <p className="text-slate-600 dark:text-slate-400">
            {step === 1 
              ? 'Enter your credentials to access your portfolio' 
              : `Enter the code sent to your email (Ref: ${otpRef})`}
          </p>
        </div>

        <div className="bg-white/60 dark:bg-white/5 backdrop-blur-[20px] p-8 rounded-3xl border border-slate-200 dark:border-white/10 shadow-2xl">
          {error && (
            <div className="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm flex items-center gap-3">
              <div className="w-1.5 h-1.5 rounded-full bg-red-500" />
              {error}
            </div>
          )}

          {step === 1 ? (
            <form onSubmit={handleLogin} className="space-y-6">
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700 dark:text-slate-300 ml-1">Username</label>
                <div className="relative group">
                  <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 group-focus-within:text-primary transition-colors" />
                  <Input
                    type="text"
                    placeholder="Enter your username"
                    className="pl-12 bg-slate-200/50 dark:bg-white/5 border-slate-300 dark:border-white/10 text-slate-900 dark:text-white placeholder:text-slate-500 focus:border-primary/50 focus:ring-primary/20 transition-all"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                    disabled={isLoading}
                  />
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between ml-1">
                  <label className="text-sm font-medium text-slate-700 dark:text-slate-300">Password</label>
                  {/* <a href="/forgot-password" className="text-xs text-primary hover:text-primary-hover transition-colors">Forgot password?</a> */}
                </div>
                <div className="relative group">
                  <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 group-focus-within:text-primary transition-colors" />
                  <Input
                    type="password"
                    placeholder="••••••••"
                    className="pl-12 bg-slate-200/50 dark:bg-white/5 border-slate-300 dark:border-white/10 text-slate-900 dark:text-white placeholder:text-slate-500 focus:border-primary/50 focus:ring-primary/20 transition-all"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    disabled={isLoading}
                  />
                </div>
              </div>
              <Button 
                type="submit" 
                className="w-full h-12 text-base font-semibold shadow-lg shadow-primary/20" 
                disabled={isLoading}
              >
                {isLoading ? (
                  <span className="flex items-center gap-2">
                    <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Authenticating...
                  </span>
                ) : (
                  <span className="flex items-center gap-2">
                    Sign In <ArrowRight className="w-4 h-4" />
                  </span>
                )}
              </Button>
            </form>
          ) : (
            <form onSubmit={handleVerifyOTP} className="space-y-6">
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-700 dark:text-slate-300 ml-1 text-center block">Enter 6-digit Code</label>
                <div className="relative group">
                  <ShieldCheck className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 group-focus-within:text-primary transition-colors" />
                  <Input
                    type="text"
                    placeholder="000000"
                    maxLength={6}
                    className="pl-12 text-center tracking-[0.5em] text-2xl font-bold bg-slate-200/50 dark:bg-white/5 border-slate-300 dark:border-white/10 text-slate-900 dark:text-white placeholder:text-slate-700 dark:placeholder:text-slate-700 focus:border-primary/50 focus:ring-primary/20 transition-all"
                    value={otpCode}
                    onChange={(e) => setOtpCode(e.target.value.replace(/\D/g, ''))}
                    required
                    disabled={isLoading}
                  />
                </div>
              </div>
              <Button 
                type="submit" 
                className="w-full h-12 text-base font-semibold shadow-lg shadow-primary/20" 
                disabled={isLoading}
              >
                {isLoading ? 'Verifying...' : 'Verify & Continue'}
              </Button>
              <button 
                type="button"
                onClick={() => setStep(1)}
                className="w-full text-sm text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 transition-colors"
                disabled={isLoading}
              >
                Go back to login
              </button>
            </form>
          )}
        </div>

        <p className="mt-8 text-center text-sm text-slate-500">
          <a href="/forgot-password" className="text-xs text-primary hover:text-primary-hover transition-colors">Forgot password?</a>
        </p>

        <p className="mt-4 text-center text-sm text-slate-500">
          
          Don&apos;t have an account? <a href="#" className="text-primary font-medium hover:underline">Request Access</a>
        </p>
      </div>
    </div>
  );
}
