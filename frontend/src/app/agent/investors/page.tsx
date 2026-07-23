'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { Search, Filter, Wallet, Users, LayoutGrid, List, AlertCircle } from 'lucide-react';
import { getAgentInvestorList, type MarketingInvestor } from '@/lib/api/investor';
import { cn } from '@/utils/cn';

export default function AgentInvestors() {
  const [investors, setInvestors] = useState<MarketingInvestor[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState('');
  const [viewMode, setViewMode] = useState<'table' | 'grid'>('table');

  const fetchInvestors = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getAgentInvestorList(status, search);
      setInvestors(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [status, search]);

  useEffect(() => {
    const timer = setTimeout(() => fetchInvestors(), 300);
    return () => clearTimeout(timer);
  }, [fetchInvestors]);

  const isExpiringSoon = (dateStr?: string) => {
    if (!dateStr) return false;
    const date = new Date(dateStr);
    const now = new Date();
    const nextMonth = new Date();
    nextMonth.setMonth(now.getMonth() + 1);
    return date <= nextMonth;
  };

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-end gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Referred Investors</h1>
          <p className="text-slate-400 mt-1">Manage and monitor investors you have referred.</p>
        </div>
        <div className="flex bg-white/5 rounded-xl p-1 border border-white/10 self-start sm:self-auto">
          <button 
            onClick={() => setViewMode('table')}
            className={cn("p-2 rounded-lg transition-all", viewMode === 'table' ? "bg-primary text-white" : "text-slate-500 hover:text-slate-300")}
          >
            <List size={18} />
          </button>
          <button 
            onClick={() => setViewMode('grid')}
            className={cn("p-2 rounded-lg transition-all", viewMode === 'grid' ? "bg-primary text-white" : "text-slate-500 hover:text-slate-300")}
          >
            <LayoutGrid size={18} />
          </button>
        </div>
      </div>

      <div className="flex flex-col md:flex-row gap-4 items-center">
        <div className="relative flex-1 group">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-primary transition-colors" size={20} />
          <input
            type="text"
            placeholder="Search by name or code..."
            className="w-full bg-white/5 border border-white/10 rounded-xl py-3 pl-10 pr-4 text-slate-100 placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="flex gap-2">
          <select 
            className="bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-slate-300 focus:outline-none focus:ring-2 focus:ring-primary/50"
            value={status}
            onChange={(e) => setStatus(e.target.value)}
          >
            <option value="">All Status</option>
            <option value="Active">Active</option>
            <option value="Pending">Pending</option>
            <option value="In Progress">In Progress</option>
          </select>
          <button className="p-3 bg-white/5 border border-white/10 rounded-xl text-slate-400 hover:text-white transition-colors">
            <Filter size={20} />
          </button>
        </div>
      </div>

      {viewMode === 'grid' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {loading ? (
               Array(6).fill(0).map((_, i) => (
                  <div key={i} className="glass h-64 animate-pulse rounded-2xl" />
               ))
          ) : investors.map((inv) => (
            <div key={inv.id} className="glass p-6 rounded-2xl border border-white/5 group hover:border-primary/30 transition-all duration-300 flex flex-col h-full">
              <div className="flex items-start justify-between mb-4">
                <div className="min-w-0">
                  <h3 className="font-bold text-lg text-slate-100 truncate pr-2">{inv.fullNameEn || inv.fullNameTh}</h3>
                  <p className="text-xs text-slate-500 font-mono mt-1">{inv.custCode}</p>
                </div>
                <span className={cn(
                  "text-[10px] px-2 py-1 rounded-full font-bold uppercase tracking-wider h-fit",
                  inv.status === 'Active' ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" : "bg-blue-500/10 text-blue-400 border border-blue-500/20"
                )}>
                  {inv.status}
                </span>
              </div>

              <div className="flex-1 space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-slate-500 flex items-center gap-1"><Wallet size={14} /> Total Value</span>
                  <span className="text-slate-100 font-bold">${Number(inv.total_amount).toLocaleString()}</span>
                </div>
                
                <div className="h-1 bg-white/5 rounded-full overflow-hidden">
                  <div className="flex h-full">
                     {inv.total_amount > 0 && (
                       <>
                          <div className="bg-emerald-500" style={{ width: `${(inv.mf_amount/inv.total_amount)*100}%` }} />
                          <div className="bg-blue-500" style={{ width: `${(inv.bond_amount/inv.total_amount)*100}%` }} />
                          <div className="bg-amber-500" style={{ width: `${(inv.pf_amount/inv.total_amount)*100}%` }} />
                       </>
                     )}
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-2 text-[10px]">
                  <div className="flex flex-col">
                      <span className="text-slate-500">MF</span>
                      <span className="text-emerald-400 font-medium">${Number(inv.mf_amount).toLocaleString()}</span>
                  </div>
                  <div className="flex flex-col">
                      <span className="text-slate-500">Bonds</span>
                      <span className="text-blue-400 font-medium">${Number(inv.bond_amount).toLocaleString()}</span>
                  </div>
                  <div className="flex flex-col">
                      <span className="text-slate-500">PF</span>
                      <span className="text-amber-400 font-medium">${Number(inv.pf_amount).toLocaleString()}</span>
                  </div>
                </div>

                {/* Compliance info in grid */}
                <div className="pt-3 flex gap-2 overflow-x-auto no-scrollbar">
                   {inv.nextKycDate && isExpiringSoon(inv.nextKycDate) && (
                     <span className="flex items-center gap-1 text-[9px] bg-rose-500/10 text-rose-400 px-2 py-1 rounded border border-rose-500/20 whitespace-nowrap">
                       <AlertCircle size={10} /> KYC Exp
                     </span>
                   )}
                   {inv.suitDate && isExpiringSoon(inv.suitDate) && (
                     <span className="flex items-center gap-1 text-[9px] bg-rose-500/10 text-rose-400 px-2 py-1 rounded border border-rose-500/20 whitespace-nowrap">
                       <AlertCircle size={10} /> Suit Exp
                     </span>
                   )}
                </div>
              </div>

              <div className="mt-6 pt-4 border-t border-white/5 flex gap-2">
                  <button className="flex-1 text-xs font-bold py-2 bg-white/5 hover:bg-white/10 rounded-lg transition-colors">Details</button>
                  <button className="flex-1 text-xs font-bold py-2 bg-primary/10 text-primary hover:bg-primary/20 rounded-lg transition-colors">Contact</button>
              </div>
            </div>
          ))}

          {!loading && investors.length === 0 && (
              <div className="col-span-full py-20 text-center">
                  <Users size={48} className="mx-auto text-slate-700 mb-4" />
                  <p className="text-slate-500 text-lg">No investors found matches your criteria</p>
              </div>
          )}
        </div>
      ) : (
        <div className="glass overflow-hidden rounded-2xl border border-white/5">
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-white/5 bg-white/5 whitespace-nowrap">
                  <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-400">Investor</th>
                  <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-400">Status</th>
                  <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-400 text-right">MF</th>
                  <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-400 text-right">Bond</th>
                  <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-400 text-right">PF</th>
                  <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-400 text-right">Total AUM</th>
                  <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-400">Compliance Expiry</th>
                  <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-slate-400 text-center">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {loading ? (
                  Array(5).fill(0).map((_, i) => (
                    <tr key={i} className="animate-pulse">
                      <td className="px-6 py-8" colSpan={8}><div className="h-4 bg-white/5 rounded w-full" /></td>
                    </tr>
                  ))
                ) : investors.map((inv) => (
                  <tr key={inv.id} className="hover:bg-white/5 transition-colors group">
                    <td className="px-6 py-4">
                      <div className="min-w-[180px]">
                        <p className="font-bold text-slate-100">{inv.fullNameEn || inv.fullNameTh}</p>
                        <p className="text-xs text-slate-500 font-mono">{inv.custCode}</p>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={cn(
                        "text-[10px] px-2 py-1 rounded-full font-bold uppercase tracking-wider inline-block",
                        inv.status === 'Active' ? "bg-emerald-500/10 text-emerald-400" : "bg-blue-500/10 text-blue-400"
                      )}>
                        {inv.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                       <p className="text-slate-300 font-medium">${Number(inv.mf_amount).toLocaleString()}</p>
                       <p className={cn(
                         "text-[10px] font-bold",
                         inv.mf_profit >= 0 ? "text-emerald-500" : "text-rose-500"
                       )}>
                         {inv.mf_profit >= 0 ? '+' : ''}{Number(inv.mf_profit).toLocaleString()}
                       </p>
                    </td>
                    <td className="px-6 py-4 text-right text-slate-300">
                       <p className="font-medium">${Number(inv.bond_amount).toLocaleString()}</p>
                       <p className="text-[10px] text-slate-600">-</p>
                    </td>
                    <td className="px-6 py-4 text-right">
                       <p className="text-slate-300 font-medium">${Number(inv.pf_amount).toLocaleString()}</p>
                       <p className={cn(
                         "text-[10px] font-bold",
                         inv.pf_profit >= 0 ? "text-emerald-500" : "text-rose-500"
                       )}>
                         {inv.pf_profit >= 0 ? '+' : ''}{Number(inv.pf_profit).toLocaleString()}
                       </p>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <p className="font-bold text-slate-100 text-lg">${Number(inv.total_amount).toLocaleString()}</p>
                      <p className={cn(
                        "text-xs font-bold",
                        inv.total_profit >= 0 ? "text-emerald-400" : "text-rose-400"
                      )}>
                        {inv.total_profit >= 0 ? '+' : ''}${Math.abs(inv.total_profit).toLocaleString()}
                      </p>
                    </td>
                    <td className="px-6 py-4">
                      <div className="space-y-1 min-w-[140px]">
                        <div className="flex justify-between items-center text-[10px]">
                           <span className="text-slate-500">KYC:</span>
                           <span className={cn(isExpiringSoon(inv.nextKycDate) ? "text-rose-400 font-bold" : "text-slate-400")}>{formatDate(inv.nextKycDate)}</span>
                        </div>
                        <div className="flex justify-between items-center text-[10px]">
                           <span className="text-slate-500">Card:</span>
                           <span className="text-slate-400">{formatDate(inv.cardExpireDate)}</span>
                        </div>
                        <div className="flex justify-between items-center text-[10px]">
                           <span className="text-slate-500">Suit:</span>
                           <span className={cn(isExpiringSoon(inv.suitDate) ? "text-rose-400 font-bold" : "text-slate-400")}>{formatDate(inv.suitDate)}</span>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <button className="text-xs font-bold py-1.5 px-3 bg-white/5 hover:bg-primary/20 hover:text-primary text-slate-400 rounded-lg transition-all">Details</button>
                    </td>
                  </tr>
                ))}
                {!loading && investors.length === 0 && (
                  <tr>
                    <td className="px-6 py-12 text-center text-slate-500" colSpan={8}>No investors found</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
