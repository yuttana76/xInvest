"use client";

import React from 'react';
import { Sidebar } from '@/components/Sidebar';
import { Navbar } from '@/components/Navbar';
import { useAuth } from '@/hooks/useAuth';
import { useRouter } from 'next/navigation';

export default function OperatorLayout({ children }: { children: React.ReactNode }) {
  const { user, isLoading, hasRole } = useAuth();
  const router = useRouter();

  const isOperator = hasRole(['operator', 'cp-risk', 'officer']);

  React.useEffect(() => {
    if (!isLoading && (!user || !isOperator)) {
      router.push('/login');
    }
  }, [user, isOperator, isLoading, router]);

  if (isLoading || !user || !isOperator) {
    return <div className="flex h-screen items-center justify-center bg-slate-950 text-white">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col">
      <Navbar />
      <div className="flex flex-1 pt-20">
        <Sidebar />
        <main className="flex-1 lg:ml-64 p-8 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
