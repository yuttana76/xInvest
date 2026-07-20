"use client";

import React, { useState } from 'react';
import { ChevronUp, ChevronDown, Newspaper, Layers } from 'lucide-react';
import { BondDetailsProps } from './types';
import { ProductNewsTab } from '@/components/fund/ProductNewsTab';

export default function BondDetails({
  balances,
  itemColor,
  expandedHoldings,
  toggleExpand,
}: BondDetailsProps) {
  const [activeTab, setActiveTab] = useState<'holdings' | 'news'>('holdings');
  
  const totalValue = balances.reduce((sum, b) => sum + (b.amount || 0), 0);

  return (
    <div className="bg-slate-50/50 dark:bg-black/20 rounded-2xl border border-slate-200 dark:border-white/5 p-6 space-y-8 animate-in fade-in duration-300">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 dark:border-white/10 pb-4">
        <div className="flex items-center gap-3">
          <div className="w-4 h-4 rounded-full min-w-4" style={{ backgroundColor: itemColor }} />
          <h3 className="text-xl font-bold text-slate-800 dark:text-slate-100">Bond Details</h3>
        </div>
        <div className="flex flex-col items-end gap-1">
          <p className="text-sm font-medium text-slate-500 dark:text-slate-400">
            Total Balance: <span className="text-slate-800 dark:text-slate-100">{new Intl.NumberFormat('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(totalValue)}</span>
          </p>
        </div>
      </div>

       {/* Tab Switcher */}
       <div className="flex gap-2 p-1 bg-slate-100 dark:bg-white/5 rounded-xl border border-slate-200 dark:border-white/10 w-fit">
        <button 
          onClick={() => setActiveTab('holdings')}
          className={`px-4 py-2 rounded-lg text-xs font-bold transition-all flex items-center gap-2 ${activeTab === 'holdings' ? 'bg-primary text-white shadow-lg' : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200'}`}
        >
          <Layers size={14} />
          HOLDINGS
        </button>
        <button 
          onClick={() => setActiveTab('news')}
          className={`px-4 py-2 rounded-lg text-xs font-bold transition-all flex items-center gap-2 ${activeTab === 'news' ? 'bg-primary text-white shadow-lg' : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200'}`}
        >
          <Newspaper size={14} />
          RELATED NEWS
        </button>
      </div>

      {activeTab === 'holdings' ? (
        <div className="space-y-4">
        <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-200">Holdings ({balances.length})</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {balances.map((b, bIdx) => {
            const holdingKey = `Bond-${bIdx}`;
            const isExpanded = expandedHoldings[holdingKey];
            const isBondActive = b.status?.toLowerCase() === 'active';

            return (
              <div key={bIdx} className="bg-slate-50 dark:bg-white/5 p-4 rounded-xl border border-slate-100 dark:border-white/5 flex flex-col gap-2 hover:bg-slate-100 dark:hover:bg-white/10 transition-all relative">
                <div className="absolute top-0 left-0 w-1 h-full rounded-l-xl" style={{ backgroundColor: itemColor }} />
                <div 
                  className="flex items-start justify-between border-b border-slate-200 dark:border-white/10 pb-2 mb-1 pl-2 cursor-pointer"
                  onClick={() => toggleExpand(holdingKey)}
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <div className="text-sm font-bold text-slate-800 dark:text-slate-200 truncate pr-2" title={b.fundCode}>
                        {b.fundCode}
                      </div>
                      <div className="text-slate-400">
                        {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                      </div>
                    </div>
                  </div>
                  
                  <div className="text-right shrink-0">
                    <div className="flex flex-col items-end gap-1">
                      <div className="text-xs text-slate-500 dark:text-slate-400">
                        Amount <span className="text-slate-800 dark:text-slate-100 font-bold ml-1">{new Intl.NumberFormat('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(b.amount)}</span>
                      </div>
                      {b.status && (
                        <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${isBondActive ? 'bg-emerald-500/10 text-emerald-600 border border-emerald-500/20' : 'bg-slate-500/10 text-slate-500 border border-slate-500/20'}`}>
                          {b.status}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {isExpanded && (
                  <div className="animate-in slide-in-from-top-1 duration-200">
                    <div className="grid grid-cols-2 gap-y-3 gap-x-4 text-xs pl-2 text-slate-500 dark:text-slate-400 pt-2 border-t border-slate-200 dark:border-white/5 mt-2">
                       <div>From Date: <span className="text-slate-800 dark:text-slate-100 block font-medium mt-1">{b.fromDate ? new Date(b.fromDate).toLocaleDateString('en-GB') : '-'}</span></div>
                       <div className="text-right">Matured Date: <span className="text-slate-800 dark:text-slate-100 block font-medium mt-1">{b.toDate ? new Date(b.toDate).toLocaleDateString('en-GB') : '-'}</span></div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
          </div>
        </div>
      ) : (
        <div className="pt-4 border-t border-slate-200 dark:border-white/5">
          <ProductNewsTab productType="bond" />
        </div>
      )}
    </div>
  );
}
