'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { Button } from '@/components/Button';
import { Input } from '@/components/Input';
import { Lock, CheckCircle2, XCircle } from 'lucide-react';
import { confirmPasswordReset } from '@/lib/auth';

function ResetPasswordForm() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');

  const uidb64 = searchParams.get('uidb64');
  const token = searchParams.get('token');

  useEffect(() => {
    if (!uidb64 || !token) {
      setStatus('error');
      setMessage('Invalid or missing password reset link.');
    }
  }, [uidb64, token]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      setStatus('error');
      setMessage('Passwords do not match.');
      return;
    }

    setStatus('loading');
    setMessage('');

    try {
      const data = await confirmPasswordReset(uidb64!, token!, newPassword);
      setStatus('success');
      setMessage(data.message);
      setTimeout(() => router.push('/login'), 3000);
    } catch (err: unknown) {
      setStatus('error');
      setMessage(typeof err === 'string' ? err : 'Failed to reset password. The link may be expired.');
    }
  };

  return (
    <div className="w-full max-w-md">
      <div className="text-center mb-10">
        <h1 className="text-3xl font-bold text-white mb-2">Reset Password</h1>
        <p className="text-slate-400">Please choose a new strong password for your account.</p>
      </div>

      <div className="glass p-8 rounded-3xl border border-white/10 shadow-2xl">
        {status === 'success' ? (
          <div className="text-center space-y-6">
            <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto">
              <CheckCircle2 className="w-8 h-8 text-green-500" />
            </div>
            <p className="text-slate-300 leading-relaxed font-medium">{message}</p>
            <p className="text-sm text-slate-500">Redirecting to login in 3 seconds...</p>
            <Button onClick={() => router.push('/login')} className="w-full">
              Go to Login Now
            </Button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-6">
            {status === 'error' && (
              <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm flex items-center gap-2">
                <XCircle className="w-4 h-4 shrink-0" />
                {message}
              </div>
            )}
            
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300 ml-1">New Password</label>
              <div className="relative group">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500 group-focus-within:text-primary transition-colors" />
                <Input
                  type="password"
                  placeholder="••••••••"
                  className="pl-12 bg-white/5 border-white/10 text-white focus:border-primary/50"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  required
                  disabled={status === 'loading' || !!message && status === 'error' && !uidb64}
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300 ml-1">Confirm New Password</label>
              <div className="relative group">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500 group-focus-within:text-primary transition-colors" />
                <Input
                  type="password"
                  placeholder="••••••••"
                  className="pl-12 bg-white/5 border-white/10 text-white focus:border-primary/50"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  disabled={status === 'loading' || !!message && status === 'error' && !uidb64}
                />
              </div>
            </div>

            <Button type="submit" className="w-full h-12" disabled={status === 'loading' || !uidb64}>
              {status === 'loading' ? 'Resetting Password...' : 'Update Password'}
            </Button>
          </form>
        )}
      </div>
    </div>
  );
}

export default function ResetPasswordPage() {
  return (
    <div className="min-h-screen flex items-center justify-center px-4 relative overflow-hidden bg-slate-950">
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary/10 blur-[120px] rounded-full -z-10" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-accent/10 blur-[120px] rounded-full -z-10" />

      <Suspense fallback={<div className="text-white">Loading...</div>}>
        <ResetPasswordForm />
      </Suspense>
    </div>
  );
}
