"use client";

import React from 'react';
import { ChevronUp, ChevronDown } from 'lucide-react';
import { BondDetailsProps } from './types';

export default function BondDetails({
  balances,
  itemColor,
  expandedHoldings,
  toggleExpand,
}: BondDetailsProps) {
  
  const totalValue = balances.reduce((sum, b) => sum + (b.amount || 0), 0);

  return (
    <div className="bg-black/20 rounded-2xl border border-white/5 p-6 space-y-8 animate-in fade-in duration-300">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/10 pb-4">
        <div className="flex items-center gap-3">
          <div className="w-4 h-4 rounded-full min-w-4" style={{ backgroundColor: itemColor }} />
          <h3 className="text-xl font-bold text-slate-100">Bond Details</h3>
        </div>
        <div className="flex flex-col items-end gap-1">
          <p className="text-sm font-medium text-slate-400">
            Total Balance: <span className="text-slate-100">{new Intl.NumberFormat('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(totalValue)}</span>
          </p>
        </div>
      </div>

      <div className="space-y-4">
        <h4 className="text-sm font-semibold text-slate-200">Holdings ({balances.length})</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {balances.map((b, bIdx) => {
            const holdingKey = `Bond-${bIdx}`;
            const isExpanded = expandedHoldings[holdingKey];
            const isBondActive = b.status?.toLowerCase() === 'active';

            return (
              <div key={bIdx} className="bg-white/5 p-4 rounded-xl border border-white/5 flex flex-col gap-2 hover:bg-white/10 transition-all relative">
                <div className="absolute top-0 left-0 w-1 h-full rounded-l-xl" style={{ backgroundColor: itemColor }} />
                <div 
                  className="flex items-start justify-between border-b border-white/10 pb-2 mb-1 pl-2 cursor-pointer"
                  onClick={() => toggleExpand(holdingKey)}
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <div className="text-sm font-bold text-slate-200 truncate pr-2" title={b.fundCode}>
                        {b.fundCode}
                      </div>
                      <div className="text-slate-500">
                        {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                      </div>
                    </div>
                  </div>
                  
                  <div className="text-right shrink-0">
                    <div className="flex flex-col items-end gap-1">
                      <div className="text-xs text-slate-400">
                        Amount <span className="text-slate-100 font-medium ml-1">{new Intl.NumberFormat('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(b.amount)}</span>
                      </div>
                      {b.status && (
                        <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${isBondActive ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-slate-500/10 text-slate-400 border border-slate-500/20'}`}>
                          {b.status}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {isExpanded && (
                  <div className="animate-in slide-in-from-top-1 duration-200">
                    <div className="grid grid-cols-2 gap-y-3 gap-x-4 text-xs pl-2 text-slate-400 pt-2 border-t border-white/5 mt-2">
                       <div>From Date: <span className="text-slate-100 block font-medium mt-1">{b.fromDate ? new Date(b.fromDate).toLocaleDateString('en-GB') : '-'}</span></div>
                       <div className="text-right">Matured Date: <span className="text-slate-100 block font-medium mt-1">{b.toDate ? new Date(b.toDate).toLocaleDateString('en-GB') : '-'}</span></div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
