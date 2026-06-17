'use client';

import React, { useEffect } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useRouter } from 'next/navigation';
import { Sidebar } from '@/components/Sidebar';

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  const userRoles = Array.isArray(user?.role) ? user.role : user?.role ? [user.role] : [];
  const hasAccess = userRoles.some(r => ['ADMIN', 'IT'].includes(r.toUpperCase()));

  useEffect(() => {
    if (!isLoading && (!isAuthenticated || !hasAccess)) {
      router.push('/login');
    }
  }, [isAuthenticated, hasAccess, isLoading, router]);

  if (isLoading || !isAuthenticated || !hasAccess) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950">
        <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex">
      <Sidebar />
      <main className="flex-1 ml-64 min-h-screen p-8">
        {children}
      </main>
    </div>
  );
}
