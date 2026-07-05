'use client';

import React, { useState, useEffect } from 'react';
import { Navbar } from '@/components/Navbar';
import Link from 'next/link';
import { getFundDetail, FundDetail } from '@/lib/api/fundDecision';
import {
  ArrowLeft,
  AlertTriangle,
  XCircle,
} from 'lucide-react';
import axios from 'axios';

// Import our new components
import { FundHeader } from '@/components/fund/FundHeader';
import { FundTabs, FundTabType } from '@/components/fund/FundTabs';
import { OverviewTab } from '@/components/fund/OverviewTab';
import { HoldingsTab } from '@/components/fund/HoldingsTab';
import { AnalysisTab } from '@/components/fund/AnalysisTab';
import { NewsTab } from '@/components/fund/NewsTab';

// ─── loading skeleton ────────────────────────────────────────────────────────

function LoadingSkeleton() {
  return (
    <section className="pt-32 pb-20 px-4 min-h-screen bg-slate-950">
      <div className="max-w-6xl mx-auto space-y-8 animate-pulse">
        {/* Header Skeleton */}
        <div className="h-48 bg-white/5 rounded-2xl border border-white/10" />
        
        {/* Tabs Skeleton */}
        <div className="h-14 bg-white/5 rounded-2xl border border-white/10 w-full max-w-2xl" />
        
        {/* Content Skeleton */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-32 bg-white/5 rounded-2xl border border-white/10" />
          ))}
        </div>
        <div className="h-64 bg-white/5 rounded-2xl border border-white/10" />
      </div>
    </section>
  );
}

// ─── not found ───────────────────────────────────────────────────────────────

function NotFound({ code }: { code: string }) {
  return (
    <section className="pt-32 pb-20 px-4 flex items-center justify-center min-h-[80vh] bg-slate-950">
      <div className="text-center space-y-8 max-w-md mx-auto group">
        <div className="w-24 h-24 mx-auto rounded-3xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center group-hover:scale-110 transition-transform duration-500">
          <AlertTriangle className="w-12 h-12 text-rose-400" />
        </div>
        <div className="space-y-3">
          <h1 className="text-4xl font-bold text-white tracking-tight">Fund Not Found</h1>
          <p className="text-slate-400 leading-relaxed">
            We couldn&apos;t locate the fund with code{' '}
            <span className="font-mono font-bold text-rose-400 bg-rose-500/10 px-2.5 py-1 rounded-lg border border-rose-500/20">
              {code}
            </span>{' '}
            in our unified investment database.
          </p>
        </div>
        <Link
          href="/discovery"
          className="inline-flex items-center gap-2 px-8 py-4 rounded-2xl bg-primary text-white font-bold hover:bg-primary/90 transition-all shadow-2xl shadow-primary/20 hover:scale-105 active:scale-95"
        >
          <ArrowLeft className="w-5 h-5" />
          Back to Explorations
        </Link>
      </div>
    </section>
  );
}

// ─── main page ───────────────────────────────────────────────────────────────

export default function FundDetailPage({ params }: { params: Promise<{ code: string }> }) {
  const [fundCode, setFundCode] = useState<string>('');
  const [fund, setFund] = useState<FundDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<FundTabType>('overview');

  useEffect(() => {
    params.then(({ code }) => {
      const decoded = decodeURIComponent(code);
      setFundCode(decoded);

      getFundDetail(decoded)
        .then((data) => {
          setFund(data);
          setLoading(false);
        })
        .catch((err) => {
          setLoading(false);
          if (axios.isAxiosError(err) && err.response?.status === 404) {
            setNotFound(true);
          } else {
            setError('System encountered an error while retrieving fund intelligence. Please refresh or try again later.');
          }
        });
    });
  }, [params]);

  if (loading) return (
    <>
      <Navbar />
      <LoadingSkeleton />
    </>
  );

  if (notFound) return (
    <>
      <Navbar />
      <NotFound code={fundCode} />
    </>
  );

  if (error) return (
    <main className="min-h-screen bg-slate-950 flex flex-col">
      <Navbar />
      <section className="flex-1 flex items-center justify-center p-4">
        <div className="text-center space-y-6 max-w-sm">
          <div className="w-16 h-16 bg-rose-500/10 rounded-2xl flex items-center justify-center mx-auto border border-rose-500/20">
            <XCircle className="w-8 h-8 text-rose-500" />
          </div>
          <p className="text-slate-300 font-medium leading-relaxed">{error}</p>
          <button 
            onClick={() => window.location.reload()}
            className="px-6 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white font-bold hover:bg-white/10 transition-all"
          >
            Retry Connection
          </button>
        </div>
      </section>
    </main>
  );

  if (!fund) return null;

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview': return <OverviewTab fund={fund} />;
      case 'holdings': return <HoldingsTab fund={fund} />;
      case 'analysis': return <AnalysisTab fund={fund} />;
      case 'news':     return <NewsTab fund={fund} />;
      default:         return <OverviewTab fund={fund} />;
    }
  };

  return (
    <main className="min-h-screen relative overflow-x-hidden bg-slate-950 text-white selection:bg-primary/30 selection:text-white">
      <Navbar />

      {/* Abstract Background Elements */}
      <div className="fixed top-0 left-0 w-full h-full -z-10 overflow-hidden pointer-events-none">
        <div className="absolute top-[-15%] left-[-10%] w-[50%] h-[50%] bg-primary/20 blur-[160px] rounded-full animate-pulse duration-[8s]" />
        <div className="absolute bottom-[-10%] right-[-5%] w-[45%] h-[45%] bg-accent/15 blur-[160px] rounded-full animate-pulse duration-[10s]" />
        <div className="absolute top-[20%] right-[10%] w-[30%] h-[30%] bg-blue-500/10 blur-[120px] rounded-full" />
      </div>

      <section className="pt-28 pb-32 px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto">
          
          {/* Navigation Path */}
          <div className="mb-8">
            <Link
              href="/discovery"
              className="inline-flex items-center gap-2 text-xs font-bold text-slate-500 hover:text-primary transition-all group uppercase tracking-widest"
            >
              <div className="p-1.5 rounded-lg bg-white/5 border border-white/10 group-hover:bg-primary/10 group-hover:border-primary/20 transition-all">
                <ArrowLeft className="w-3 h-3 group-hover:-translate-x-0.5 transition-transform" />
              </div>
              Back to Marketplace
            </Link>
          </div>

          <FundHeader fund={fund} />
          
          <FundTabs 
            activeTab={activeTab} 
            setActiveTab={setActiveTab} 
            newsCount={fund.approved_news?.length} 
          />

          <div className="min-h-[400px]">
             {renderTabContent()}
          </div>

        </div>
      </section>

      {/* Footer Decoration */}
      <footer className="py-12 border-t border-white/5 bg-slate-950/50 backdrop-blur-xl">
         <div className="max-w-6xl mx-auto px-4 flex flex-col md:flex-row justify-between items-center gap-6">
            <div className="flex items-center gap-3">
               <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center font-bold">{APP_NAME_BADGE.toUpperCase()}</div>
               <span className="text-sm font-bold tracking-tighter">{APP_NAME} Intelligence</span>
            </div>
            <p className="text-xs text-slate-500 font-medium tracking-wide">
               &copy; 2026 {APP_NAME}. Market data provided &quot;as-is&quot; for informational purposes.
            </p>
         </div>
      </footer>
    </main>
  );
}
