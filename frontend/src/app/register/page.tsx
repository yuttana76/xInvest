'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/Button';
import { Input } from '@/components/Input';
import { User, Mail, Lock, Phone, ArrowRight, ShieldCheck, RefreshCw, KeyRound, CheckCircle } from 'lucide-react';
import axios from 'axios';
import { authApi } from '@/lib/auth';
import { z } from 'zod';
import Link from 'next/link';

// Define Zod Validation Schema for Registration Form
const registerSchema = z.object({
  username: z.string()
    .min(3, { message: 'Username must be at least 3 characters long' })
    .max(50, { message: 'Username is too long' })
    .regex(/^[a-zA-Z0-9_]+$/, { message: 'Username can only contain letters, numbers, and underscores' }),
  email: z.string()
    .min(1, { message: 'Email is required' })
    .email({ message: 'Invalid email address' }),
  first_name: z.string().min(1, { message: 'First name is required' }),
  last_name: z.string().min(1, { message: 'Last name is required' }),
  mobile_number: z.string()
    .regex(/^0[0-9]{8,9}$/, { message: 'Mobile number must be a valid Thai format (e.g. 0812345678)' }),
  password: z.string()
    .min(8, { message: 'Password must be at least 8 characters long' })
    .regex(/[A-Z]/, { message: 'Password must contain at least one uppercase letter' })
    .regex(/[a-z]/, { message: 'Password must contain at least one lowercase letter' })
    .regex(/[0-9]/, { message: 'Password must contain at least one number' })
    .regex(/[^A-Za-z0-9]/, { message: 'Password must contain at least one special character' }),
  password_confirm: z.string()
}).refine((data) => data.password === data.password_confirm, {
  message: 'Passwords do not match',
  path: ['password_confirm']
});

type RegisterFormData = z.infer<typeof registerSchema>;

export default function RegisterPage() {
  const router = useRouter();
  const [step, setStep] = useState(1); // 1: Form, 2: OTP, 3: Success
  const [formData, setFormData] = useState<Partial<RegisterFormData>>({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    mobile_number: '',
    password: '',
    password_confirm: '',
  });

  const [formErrors, setFormErrors] = useState<Partial<Record<keyof RegisterFormData, string>>>({});
  const [otpCode, setOtpCode] = useState('');
  const [apiError, setApiError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [otpRef, setOtpRef] = useState('');
  
  // Timer for Resend OTP button
  const [resendCooldown, setResendCooldown] = useState(0);

  useEffect(() => {
    if (resendCooldown <= 0) return;
    const timer = setInterval(() => {
      setResendCooldown((prev) => prev - 1);
    }, 1000);
    return () => clearInterval(timer);
  }, [resendCooldown]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    // Clear validation error when typing
    if (formErrors[name as keyof RegisterFormData]) {
      setFormErrors((prev) => ({ ...prev, [name]: undefined }));
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setApiError('');
    setFormErrors({});

    // Validate using Zod
    const result = registerSchema.safeParse(formData);
    if (!result.success) {
      const errors: Partial<Record<keyof RegisterFormData, string>> = {};
      result.error.issues.forEach((issue) => {
        const path = issue.path[0] as keyof RegisterFormData;
        if (path) {
          errors[path] = issue.message;
        }
      });
      setFormErrors(errors);
      setIsLoading(false);
      return;
    }

    try {
      const response = await authApi.post('/api/v1/auth/register/', result.data);
      setOtpRef(response.data.otp_ref);
      setStep(2);
    } catch (err: unknown) {
      if (axios.isAxiosError(err)) {
        // Handle field-specific validation errors returned from Backend Django serializer
        const backendErrors = err.response?.data;
        if (backendErrors && typeof backendErrors === 'object') {
          const errors: Partial<Record<keyof RegisterFormData, string>> = {};
          let msg = '';
          Object.entries(backendErrors).forEach(([key, val]) => {
            if (key in formData) {
              errors[key as keyof RegisterFormData] = Array.isArray(val) ? val[0] : String(val);
            } else {
              msg = Array.isArray(val) ? val[0] : String(val);
            }
          });
          setFormErrors(errors);
          if (msg) {
            setApiError(msg);
          } else if (Object.keys(errors).length > 0) {
            setApiError('Please fix the errors below.');
          } else {
            setApiError(err.response?.data?.error || 'Registration failed');
          }
        } else {
          setApiError(err.response?.data?.error || 'Registration failed');
        }
      } else {
        setApiError('An unexpected error occurred.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerifyOTP = async (e: React.FormEvent) => {
    e.preventDefault();
    if (otpCode.length !== 6) {
      setApiError('OTP code must be 6 digits.');
      return;
    }

    setIsLoading(true);
    setApiError('');
    try {
      await authApi.post('/api/v1/auth/register/verify/', {
        username: formData.username,
        otp_code: otpCode,
      });
      setStep(3);
      // Auto redirect to login page after 3 seconds
      setTimeout(() => {
        router.push('/login');
      }, 3000);
    } catch (err: unknown) {
      if (axios.isAxiosError(err)) {
        setApiError(err.response?.data?.error || 'OTP verification failed');
      } else {
        setApiError('OTP verification failed');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleResendOTP = async () => {
    if (resendCooldown > 0) return;
    setIsLoading(true);
    setApiError('');
    try {
      const response = await authApi.post('/api/v1/auth/register/resend-otp/', {
        username: formData.username,
      });
      setOtpRef(response.data.otp_ref);
      setResendCooldown(60); // 60 seconds cooldown
    } catch (err: unknown) {
      if (axios.isAxiosError(err)) {
        setApiError(err.response?.data?.error || 'Failed to resend OTP');
      } else {
        setApiError('Failed to resend OTP');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12 relative overflow-hidden bg-slate-50 dark:bg-slate-950 transition-colors duration-300 text-slate-900 dark:text-white">
      {/* Background Decor */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary/20 dark:bg-primary/10 blur-[120px] rounded-full -z-10" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-accent/20 dark:bg-accent/10 blur-[120px] rounded-full -z-10" />

      <div className="w-full max-w-lg">
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center gap-2 mb-4 hover:opacity-80 transition-opacity">
            <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center shadow-lg shadow-primary/20">
              <span className="text-white font-bold text-xl text-center">x</span>
            </div>
            <span className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">Invest</span>
          </Link>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">
            {step === 1 ? 'Create Account' : step === 2 ? 'Email Verification' : 'Registration Complete!'}
          </h1>
          <p className="text-slate-600 dark:text-slate-400">
            {step === 1 
              ? 'Join xInvest to optimize your wealth portfolio' 
              : step === 2 
                ? `Enter the code sent to your email (Ref: ${otpRef})`
                : 'Your email has been verified successfully.'}
          </p>
        </div>

        <div className="bg-white/60 dark:bg-white/5 backdrop-blur-[20px] p-8 rounded-3xl border border-slate-200 dark:border-white/10 shadow-2xl">
          {apiError && (
            <div className="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm flex items-center gap-3">
              <div className="w-1.5 h-1.5 rounded-full bg-red-500" />
              {apiError}
            </div>
          )}

          {step === 1 && (
            <form onSubmit={handleRegister} className="space-y-5">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-xs font-medium text-slate-700 dark:text-slate-300 ml-1">First Name</label>
                  <Input
                    name="first_name"
                    type="text"
                    placeholder="John"
                    value={formData.first_name}
                    onChange={handleChange}
                    disabled={isLoading}
                    required
                  />
                  {formErrors.first_name && <p className="text-xs text-red-500 ml-1">{formErrors.first_name}</p>}
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-medium text-slate-700 dark:text-slate-300 ml-1">Last Name</label>
                  <Input
                    name="last_name"
                    type="text"
                    placeholder="Doe"
                    value={formData.last_name}
                    onChange={handleChange}
                    disabled={isLoading}
                    required
                  />
                  {formErrors.last_name && <p className="text-xs text-red-500 ml-1">{formErrors.last_name}</p>}
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-xs font-medium text-slate-700 dark:text-slate-300 ml-1">Username</label>
                <div className="relative group">
                  <User className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 group-focus-within:text-primary transition-colors" />
                  <Input
                    name="username"
                    type="text"
                    placeholder="username123"
                    className="pl-11"
                    value={formData.username}
                    onChange={handleChange}
                    disabled={isLoading}
                    required
                  />
                </div>
                {formErrors.username && <p className="text-xs text-red-500 ml-1">{formErrors.username}</p>}
              </div>

              <div className="space-y-1">
                <label className="text-xs font-medium text-slate-700 dark:text-slate-300 ml-1">Email</label>
                <div className="relative group">
                  <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 group-focus-within:text-primary transition-colors" />
                  <Input
                    name="email"
                    type="email"
                    placeholder="name@example.com"
                    className="pl-11"
                    value={formData.email}
                    onChange={handleChange}
                    disabled={isLoading}
                    required
                  />
                </div>
                {formErrors.email && <p className="text-xs text-red-500 ml-1">{formErrors.email}</p>}
              </div>

              <div className="space-y-1">
                <label className="text-xs font-medium text-slate-700 dark:text-slate-300 ml-1">Mobile Number</label>
                <div className="relative group">
                  <Phone className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 group-focus-within:text-primary transition-colors" />
                  <Input
                    name="mobile_number"
                    type="tel"
                    placeholder="0812345678"
                    className="pl-11"
                    value={formData.mobile_number}
                    onChange={handleChange}
                    disabled={isLoading}
                    required
                  />
                </div>
                {formErrors.mobile_number && <p className="text-xs text-red-500 ml-1">{formErrors.mobile_number}</p>}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-xs font-medium text-slate-700 dark:text-slate-300 ml-1">Password</label>
                  <div className="relative group">
                    <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 group-focus-within:text-primary transition-colors" />
                    <Input
                      name="password"
                      type="password"
                      placeholder="••••••••"
                      className="pl-11 text-xs"
                      value={formData.password}
                      onChange={handleChange}
                      disabled={isLoading}
                      required
                    />
                  </div>
                  {formErrors.password && <p className="text-xs text-red-500 ml-1 leading-snug">{formErrors.password}</p>}
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-medium text-slate-700 dark:text-slate-300 ml-1">Confirm Password</label>
                  <div className="relative group">
                    <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 group-focus-within:text-primary transition-colors" />
                    <Input
                      name="password_confirm"
                      type="password"
                      placeholder="••••••••"
                      className="pl-11 text-xs"
                      value={formData.password_confirm}
                      onChange={handleChange}
                      disabled={isLoading}
                      required
                    />
                  </div>
                  {formErrors.password_confirm && <p className="text-xs text-red-500 ml-1 leading-snug">{formErrors.password_confirm}</p>}
                </div>
              </div>

              <Button 
                type="submit" 
                className="w-full h-12 text-base font-semibold shadow-lg shadow-primary/20 mt-4" 
                disabled={isLoading}
              >
                {isLoading ? (
                  <span className="flex items-center gap-2 justify-center">
                    <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Creating account...
                  </span>
                ) : (
                  <span className="flex items-center gap-2 justify-center">
                    Register <ArrowRight className="w-4 h-4" />
                  </span>
                )}
              </Button>
            </form>
          )}

          {step === 2 && (
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

              <div className="flex items-center justify-between text-sm px-1">
                <span className="text-slate-500">Didn&apos;t receive the code?</span>
                <button
                  type="button"
                  onClick={handleResendOTP}
                  disabled={isLoading || resendCooldown > 0}
                  className="flex items-center gap-1.5 font-medium text-primary hover:text-primary-hover disabled:text-slate-400 dark:disabled:text-slate-600 transition-colors"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
                  {resendCooldown > 0 ? `Resend in ${resendCooldown}s` : 'Resend OTP'}
                </button>
              </div>

              <Button 
                type="submit" 
                className="w-full h-12 text-base font-semibold shadow-lg shadow-primary/20" 
                disabled={isLoading}
              >
                {isLoading ? 'Verifying...' : 'Verify & Activate'}
              </Button>
              
              <button 
                type="button"
                onClick={() => setStep(1)}
                className="w-full text-sm text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 transition-colors"
                disabled={isLoading}
              >
                Go back to Registration
              </button>
            </form>
          )}

          {step === 3 && (
            <div className="py-8 text-center space-y-6">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-green-500/10 border border-green-500/20 text-green-500 rounded-full">
                <CheckCircle className="w-10 h-10" />
              </div>
              <div className="space-y-2">
                <h3 className="text-2xl font-bold text-slate-900 dark:text-white">Email Verified!</h3>
                <p className="text-slate-600 dark:text-slate-400">
                  Your account is now active and ready. You will be redirected to the login page shortly.
                </p>
              </div>
              <div className="pt-4">
                <Button 
                  onClick={() => router.push('/login')}
                  className="w-full h-11 font-medium"
                >
                  Go to Login Now
                </Button>
              </div>
            </div>
          )}
        </div>

        <p className="mt-8 text-center text-sm text-slate-500">
          Already have an account?{' '}
          <a href="/login" className="text-primary font-medium hover:underline">
            Sign In
          </a>
        </p>
      </div>
    </div>
  );
}
