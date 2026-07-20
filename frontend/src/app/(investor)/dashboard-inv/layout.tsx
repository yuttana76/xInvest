'use client';

import React, { useEffect, useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useRouter } from 'next/navigation';
import { LogOut, User as UserIcon } from 'lucide-react';
import { Button } from '@/components/Button';
import { ThemeToggle } from '@/components/ThemeToggle';
import { LogoutConfirmModal } from '@/components/LogoutConfirmModal';

export default function InvestorLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, isAuthenticated, isLoading, logout, hasRole } = useAuth();
  const router = useRouter();
  const [isLogoutModalOpen, setIsLogoutModalOpen] = useState(false);

  const isInvestor = hasRole('investor');

  useEffect(() => {
    if (!isLoading && (!isAuthenticated || !isInvestor)) {
      router.push('/login');
    }
  }, [isAuthenticated, isInvestor, isLoading, router]);

  const handleLogout = () => {
    setIsLogoutModalOpen(false);
    logout();
  };

  if (isLoading || !isAuthenticated || !isInvestor) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Investor Header */}
      <header className="glass border-b border-white/5 dark:border-white/5 h-16 flex items-center px-6 md:px-12 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto w-full flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center rotate-12">
              <span className="text-white font-bold text-lg -rotate-12">x</span>
            </div>
            <span className="text-xl font-bold tracking-tight">Dashboard</span>
          </div>

          <div className="flex items-center gap-4">
            <ThemeToggle />
            <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10">
              <UserIcon className="w-4 h-4 text-primary" />
              <span className="text-sm font-medium text-slate-600 dark:text-slate-300">{user?.username}</span>
            </div>
            <Button variant="ghost" size="sm" className="gap-2 text-slate-500 dark:text-slate-400 hover:text-red-600 dark:hover:text-red-400" onClick={() => setIsLogoutModalOpen(true)}>
              <LogOut size={16} />
              <span className="hidden sm:inline">Sign Out</span>
            </Button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 md:px-12 py-8">
        {children}
      </main>

      <LogoutConfirmModal 
        isOpen={isLogoutModalOpen} 
        onClose={() => setIsLogoutModalOpen(false)} 
        onConfirm={handleLogout} 
      />
    </div>
  );
}
