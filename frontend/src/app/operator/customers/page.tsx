"use client";

import React, { useEffect, useState, useCallback } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useRouter } from 'next/navigation';
import { getOperatorInvestorList, exportOperatorInvestors, type MarketingInvestor } from '@/lib/api/investor';
import { Search, User, ChevronRight, FileDown, ChevronLeft } from 'lucide-react';
import { Button } from '@/components/Button';
import { Input } from '@/components/Input';
import { cn } from '@/utils/cn';

export default function OperatorCustomers() {
  const { user } = useAuth();
  const router = useRouter();
  const [investors, setInvestors] = useState<MarketingInvestor[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [page, setPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);

  const fetchInvestors = useCallback(async (pageNum: number) => {
    setLoading(true);
    try {
      const data = await getOperatorInvestorList(pageNum, statusFilter, search);
      setInvestors(data.results);
      setTotalCount(data.count);
      setPage(pageNum);
    } catch (error) {
      console.error('Failed to fetch investors:', error);
    } finally {
      setLoading(false);
    }
  }, [statusFilter, search]);

  useEffect(() => {
    if (user && user.role === 'operator') {
      const timer = setTimeout(() => fetchInvestors(1), 300);
      return () => clearTimeout(timer);
    }
  }, [fetchInvestors, user]);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    fetchInvestors(1);
  };

  const handleExport = async () => {
    try {
      await exportOperatorInvestors();
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

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

  const totalPages = Math.ceil(totalCount / 20);

  return (
    <div className="text-slate-100">
      <div className="max-w-7xl mx-auto px-4 pb-12">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-8">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Customer Management</h1>
            <p className="text-slate-400 mt-1">Total {totalCount} investors registered.</p>
          </div>
          
          <div className="flex items-center gap-4">
             <Button variant="outline" className="flex items-center gap-2" onClick={handleExport}>
                <FileDown size={18} />
                Export to Excel
             </Button>
             <div className="bg-emerald-500/10 text-emerald-400 px-4 py-2 rounded-xl border border-emerald-500/20 text-sm font-medium">
               Operator Mode
             </div>
          </div>
        </div>

        {/* Filters */}
        <div className="glass p-6 rounded-2xl border border-white/5 mb-8">
          <form onSubmit={handleSearch} className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
              <Input 
                placeholder="Search by name or customer code..." 
                className="pl-10"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <div className="w-full md:w-48">
              <select 
                className="w-full h-10 bg-white/5 border border-white/10 rounded-lg px-3 text-sm outline-none focus:border-primary transition-colors text-slate-300"
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                <option value="">All Status</option>
                <option value="Active">Active</option>
                <option value="Inactive">Inactive</option>
              </select>
            </div>
            <Button type="submit">Search</Button>
          </form>
        </div>

        {/* Investor List */}
        <div className="glass rounded-2xl border border-white/5 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-white/5 border-b border-white/10 whitespace-nowrap">
                  <th className="px-6 py-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Investor</th>
                  <th className="px-6 py-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-4 text-xs font-semibold text-slate-400 uppercase tracking-wider text-right">MF</th>
                  <th className="px-6 py-4 text-xs font-semibold text-slate-400 uppercase tracking-wider text-right">Bond</th>
                  <th className="px-6 py-4 text-xs font-semibold text-slate-400 uppercase tracking-wider text-right">PF</th>
                  <th className="px-6 py-4 text-xs font-semibold text-slate-400 uppercase tracking-wider text-right">Total AUM</th>
                  <th className="px-6 py-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Compliance Expiry</th>
                  <th className="px-6 py-4 text-xs font-semibold text-slate-400 uppercase tracking-wider text-center">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {loading ? (
                   Array(5).fill(0).map((_, i) => (
                    <tr key={i} className="animate-pulse">
                      <td colSpan={8} className="px-6 py-8"><div className="h-4 bg-white/5 rounded w-full" /></td>
                    </tr>
                  ))
                ) : investors.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="px-6 py-12 text-center text-slate-500 italic">
                      No investors found matching your criteria.
                    </td>
                  </tr>
                ) : (
                  investors.map((investor) => (
                    <tr key={investor.custCode} className="hover:bg-white/5 transition-colors group">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                            <User size={16} />
                          </div>
                          <div className="min-w-[140px]">
                            <p className="font-semibold text-slate-100">{investor.fullNameEn || investor.fullNameTh}</p>
                            <p className="font-mono text-[10px] text-slate-400">{investor.custCode}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider border ${
                          investor.status === 'Active' 
                            ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' 
                            : 'bg-slate-500/10 text-slate-400 border-slate-500/20'
                        }`}>
                          {investor.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right">
                         <p className="text-slate-300 font-medium">${Number(investor.mf_amount).toLocaleString()}</p>
                         <p className={cn(
                           "text-[10px] font-bold",
                           investor.mf_profit >= 0 ? "text-emerald-500" : "text-rose-500"
                         )}>
                           {investor.mf_profit >= 0 ? '+' : ''}{Number(investor.mf_profit).toLocaleString()}
                         </p>
                      </td>
                      <td className="px-6 py-4 text-right">
                         <p className="text-slate-300 font-medium">${Number(investor.bond_amount).toLocaleString()}</p>
                         <p className="text-[10px] text-slate-600">-</p>
                      </td>
                      <td className="px-6 py-4 text-right">
                         <p className="text-slate-300 font-medium">${Number(investor.pf_amount).toLocaleString()}</p>
                         <p className={cn(
                           "text-[10px] font-bold",
                           investor.pf_profit >= 0 ? "text-emerald-500" : "text-rose-500"
                         )}>
                           {investor.pf_profit >= 0 ? '+' : ''}{Number(investor.pf_profit).toLocaleString()}
                         </p>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <p className="font-bold text-slate-100 text-lg">${Number(investor.total_amount).toLocaleString()}</p>
                        <p className={cn(
                          "text-xs font-bold",
                          investor.total_profit >= 0 ? "text-emerald-400" : "text-rose-400"
                        )}>
                          {investor.total_profit >= 0 ? '+' : ''}${Math.abs(investor.total_profit).toLocaleString()}
                        </p>
                      </td>
                      <td className="px-6 py-4">
                        <div className="space-y-1 min-w-[140px]">
                          <div className="flex justify-between items-center text-[10px]">
                             <span className="text-slate-500">KYC:</span>
                             <span className={cn(isExpiringSoon(investor.nextKycDate) ? "text-rose-400 font-bold" : "text-slate-400")}>{formatDate(investor.nextKycDate)}</span>
                          </div>
                          <div className="flex justify-between items-center text-[10px]">
                             <span className="text-slate-500">Card:</span>
                             <span className="text-slate-400">{formatDate(investor.cardExpireDate)}</span>
                          </div>
                          <div className="flex justify-between items-center text-[10px]">
                             <span className="text-slate-500">Suit:</span>
                             <span className={cn(isExpiringSoon(investor.suitDate) ? "text-rose-400 font-bold" : "text-slate-400")}>{formatDate(investor.suitDate)}</span>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-center">
                        <Button 
                          variant="ghost" 
                          size="sm" 
                          className="text-slate-400 hover:text-white"
                          onClick={() => router.push(`/operator/investor/${investor.custCode}`)}
                        >
                          Details <ChevronRight size={14} className="ml-1" />
                        </Button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination Controls */}
          {!loading && totalPages > 1 && (
            <div className="px-6 py-4 border-t border-white/10 flex items-center justify-between bg-white/5">
                <div className="text-sm text-slate-500">
                    Showing <span className="text-slate-300">{(page - 1) * 20 + 1}</span> to <span className="text-slate-300">{Math.min(page * 20, totalCount)}</span> of <span className="text-slate-300">{totalCount}</span>
                </div>
                <div className="flex items-center gap-2">
                    <Button 
                        variant="outline" 
                        size="sm" 
                        disabled={page === 1}
                        onClick={() => fetchInvestors(page - 1)}
                    >
                        <ChevronLeft size={16} />
                    </Button>
                    <div className="flex items-center gap-1">
                      {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                          const p = i + 1;
                          return (
                              <Button 
                                  key={p}
                                  variant={page === p ? 'primary' : 'ghost'} 
                                  size="sm"
                                  className="w-8 h-8 p-0"
                                  onClick={() => fetchInvestors(p)}
                              >
                                  {p}
                              </Button>
                          );
                      })}
                    </div>
                    {totalPages > 5 && <span className="text-slate-500">...</span>}
                    <Button 
                        variant="outline" 
                        size="sm" 
                        disabled={page === totalPages}
                        onClick={() => fetchInvestors(page + 1)}
                    >
                        <ChevronRight size={16} />
                    </Button>
                </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
