'use client';

import React, { useState } from 'react';
import { Button } from '@/components/Button';
import { Input } from '@/components/Input';
import { ArrowLeft, Send, User } from 'lucide-react';
import Link from 'next/link';
import { requestPasswordReset } from '@/lib/auth';

export default function ForgotPasswordPage() {
  const [username, setUsername] = useState('');
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus('loading');
    setMessage('');

    try {
      const data = await requestPasswordReset(username);
      setStatus('success');
      setMessage(data.message);
    } catch (err: unknown) {
      setStatus('error');
      setMessage(typeof err === 'string' ? err : 'Something went wrong. Please try again.');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 relative overflow-hidden bg-slate-950">
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary/10 blur-[120px] rounded-full -z-10" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-secondary/10 blur-[120px] rounded-full -z-10" />

      <div className="w-full max-w-md">
        <div className="text-center mb-10">
          <Link href="/login" className="inline-flex items-center gap-2 text-slate-400 hover:text-white transition-colors mb-6 group">
            <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
            Back to Login
          </Link>
          <h1 className="text-3xl font-bold text-white mb-2">Forgot Password?</h1>
          <p className="text-slate-400">Enter your username and we&apos;ll send you a link to reset your password.</p>
        </div>

        <div className="glass p-8 rounded-3xl border border-white/10 shadow-2xl">
          {status === 'success' ? (
            <div className="text-center space-y-6">
              <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto">
                <Send className="w-8 h-8 text-green-500" />
              </div>
              <p className="text-slate-300 leading-relaxed">{message}</p>
              <Button onClick={() => window.location.href = '/login'} className="w-full">
                Return to Login
              </Button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-6">
              {status === 'error' && (
                <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
                  {message}
                </div>
              )}
              <div className="space-y-2">
                <label className="text-sm font-medium text-slate-300 ml-1">Username</label>
                <div className="relative group">
                  <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500 group-focus-within:text-primary transition-colors" />
                  <Input
                    type="text"
                    placeholder="Enter your username"
                    className="pl-12 bg-white/5 border-white/10 text-white placeholder:text-slate-600 focus:border-primary/50 focus:ring-primary/20 transition-all"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                    disabled={status === 'loading'}
                  />
                </div>
              </div>
              <Button type="submit" className="w-full h-12" disabled={status === 'loading'}>
                {status === 'loading' ? 'Sending Link...' : 'Send Reset Link'}
              </Button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
