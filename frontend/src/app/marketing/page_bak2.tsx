"use client";

import React from 'react';
import { useAuth } from '@/hooks/useAuth';
import { LayoutDashboard, Users, BarChart3, ChevronRight, Sparkles } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function OperatorWelcome() {
  const { user } = useAuth();
  const router = useRouter();

  const quicklinks = [
    { 
        title: "Dashboard", 
        desc: "View real-time statistics and alerts", 
        icon: <LayoutDashboard className="text-blue-400" />, 
        href: "/operator/dashboard",
        color: "blue"
    },
    { 
        title: "Customers", 
        desc: "Manage and export investor list", 
        icon: <Users className="text-emerald-400" />, 
        href: "/operator/customers",
        color: "emerald"
    },
    { 
        title: "Reports", 
        desc: "Generate and download system reports", 
        icon: <BarChart3 className="text-amber-400" />, 
        href: "/operator/reports",
        color: "amber"
    },
  ];

  return (
    <div className="flex flex-col items-center justify-center min-h-[80vh] text-center px-4">
      <div className="mb-8 relative">
        <div className="absolute -inset-4 bg-primary/20 blur-3xl rounded-full opacity-50 animate-pulse"></div>
        <div className="w-20 h-20 bg-primary/10 border border-primary/20 rounded-3xl flex items-center justify-center relative">
            <Sparkles size={40} className="text-primary" />
        </div>
      </div>

      <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-4">
        Welcome back, <span className="text-primary">{user?.username}</span>
      </h1>
      <p className="text-slate-400 text-lg max-w-2xl mb-12">
        We&apos;ve updated the Operator portal with a new side navigation. 
        You can now manage customers, view analytics, and generate reports more efficiently.
      </p>

      {/* <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-4xl">
        {quicklinks.map((link, idx) => (
          <div 
            key={idx}
            className="glass p-6 rounded-2xl border border-white/5 hover:border-primary/30 transition-all duration-300 cursor-pointer text-left group"
            onClick={() => router.push(link.href)}
          >
            <div className={`p-3 rounded-xl bg-${link.color}-500/10 mb-4 w-fit group-hover:scale-110 transition-transform`}>
                {link.icon}
            </div>
            <h3 className="text-xl font-semibold mb-2 flex items-center justify-between">
                {link.title}
                <ChevronRight size={18} className="text-slate-600 group-hover:text-primary transition-colors" />
            </h3>
            <p className="text-sm text-slate-500 leading-relaxed">
                {link.desc}
            </p>
          </div>
        ))}
      </div> */}

      <div className="mt-16 text-slate-500 text-sm flex items-center gap-2">
        <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
        System Status: Marketing
      </div>
    </div>
  );
}
