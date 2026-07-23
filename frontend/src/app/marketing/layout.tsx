'use client';

import React, { useEffect } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useRouter } from 'next/navigation';
import { Sidebar } from '@/components/Sidebar';
import { Navbar } from '@/components/Navbar';

export default function MarketingLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, isAuthenticated, isLoading, hasRole } = useAuth();
  const router = useRouter();

  const isMarketing = hasRole(['marketing', 'ceo']);

  useEffect(() => {
    if (!isLoading && (!isAuthenticated || !isMarketing)) {
      router.push('/login');
    }
  }, [isAuthenticated, isMarketing, isLoading, router]);

  if (isLoading || !isAuthenticated || !isMarketing) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950">
        <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <Sidebar />
      <main className="lg:pl-64 pt-20">
        <div className="p-8 max-w-7xl mx-auto">
          {children}
        </div>
      </main>
    </div>
  );
}
