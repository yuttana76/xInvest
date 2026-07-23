'use client';

import React, { useEffect } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useRouter, usePathname } from 'next/navigation';
import { Sidebar } from '@/components/Sidebar';
import { Navbar } from '@/components/Navbar';
import Link from 'next/link';
import { Building2, FileScan, Receipt, Boxes } from 'lucide-react';

const NAV_ITEMS = [
  { href: '/payment/suppliers', label: 'Suppliers', icon: Building2 },
  { href: '/payment/documents', label: 'Documents', icon: FileScan },
  { href: '/payment/vouchers', label: 'Vouchers', icon: Receipt },
  { href: '/payment/assets', label: 'Assets', icon: Boxes },
];

export default function PaymentLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading || !isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950">
        <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background text-foreground transition-colors duration-300">
      <Navbar />
      <Sidebar />
      <main className="lg:pl-64 pt-20">
        <div className="p-8 max-w-7xl mx-auto">
          <div className="mb-6 flex items-center gap-2 border-b border-gray-200 dark:border-gray-800 pb-4 overflow-x-auto">
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon;
              const isActive = pathname?.startsWith(item.href);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-colors shrink-0 ${
                    isActive
                      ? 'bg-primary/10 text-primary'
                      : 'text-gray-500 hover:bg-gray-100 dark:hover:bg-white/5'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {item.label}
                </Link>
              );
            })}
          </div>
          {children}
        </div>
      </main>
    </div>
  );
}
