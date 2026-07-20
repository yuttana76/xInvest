"use client";

import React, { useEffect, useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useRouter } from 'next/navigation';
import { getOperatorDashboardStats, type OperatorDashboardStats } from '@/lib/api/investor';
import { Users, UserPlus, UserCheck, AlertTriangle, ChevronRight, TrendingUp } from 'lucide-react';
import { Button } from '@/components/Button';

export default function OperatorDashboard() {
  const { user, hasRole } = useAuth();
  const router = useRouter();
  const [data, setData] = useState<OperatorDashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchRef = React.useRef(false);

  useEffect(() => {
    if (fetchRef.current) return;
    
    const fetchStats = async () => {
      setLoading(true);
      try {
        const stats = await getOperatorDashboardStats();
        setData(stats);
      } catch (error) {
        console.error('Failed to fetch dashboard stats:', error);
      } finally {
        setLoading(false);
      }
    };

    if (user && hasRole('operator')) {
      fetchRef.current = true;
      fetchStats();
    }
  }, [user, hasRole]);

  if (loading && !data) {
    return <div className="flex h-full items-center justify-center">Loading stats...</div>;
  }

  if (!data) return null;

  const stats = data.stats;

  return (
    <div className="text-slate-100">
        <div className="mb-8 flex justify-between items-end">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Operator Dashboard</h1>
            <p className="text-slate-400 mt-1">System-wide investor activity and compliance monitoring.</p>
          </div>
          <div className="bg-emerald-500/10 text-emerald-400 px-4 py-2 rounded-xl border border-emerald-500/20 text-sm font-medium">
             Operator Mode
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="glass p-6 rounded-2xl border border-white/5 relative overflow-hidden group">
                <div className="flex justify-between items-start mb-4">
                    <div className="p-3 rounded-xl bg-blue-500/10 text-blue-400">
                        <Users size={24} />
                    </div>
                    <div className="text-xs font-medium text-slate-500 uppercase tracking-wider">Total Customers</div>
                </div>
                <div className="text-4xl font-bold">{stats.totalCustomers.toLocaleString()}</div>
                <div className="mt-2 flex items-center gap-2 text-xs">
                    <span className="text-emerald-400 flex items-center">
                        <TrendingUp size={12} className="mr-1" />
                        Live
                    </span>
                    <span className="text-slate-500">Global count</span>
                </div>
            </div>

            <div className="glass p-6 rounded-2xl border border-white/5 relative overflow-hidden group">
                <div className="flex justify-between items-start mb-4">
                    <div className="p-3 rounded-xl bg-emerald-500/10 text-emerald-400">
                        <UserPlus size={24} />
                    </div>
                    <div className="text-xs font-medium text-slate-500 uppercase tracking-wider">New Today</div>
                </div>
                <div className="text-4xl font-bold">{stats.newToday}</div>
                <div className="mt-2 text-xs text-slate-500">Joined in the last 24 hours</div>
            </div>

            <div className="glass p-6 rounded-2xl border border-white/5 relative overflow-hidden group">
                <div className="flex justify-between items-start mb-4">
                    <div className="p-3 rounded-xl bg-amber-500/10 text-amber-400">
                        <UserCheck size={24} />
                    </div>
                    <div className="text-xs font-medium text-slate-500 uppercase tracking-wider">Updated Today</div>
                </div>
                <div className="text-4xl font-bold">{stats.modifiedToday}</div>
                <div className="mt-2 text-xs text-slate-500">Profiles modified today</div>
            </div>
        </div>

        {/* Expirations Section */}
        <div className="mb-8">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <AlertTriangle size={20} className="text-amber-500" />
                Monthly Compliance Alerts
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="glass p-5 rounded-xl border border-white/5 hover:border-white/10 transition-colors">
                    <p className="text-sm text-slate-400 mb-1">Suitability Expirations</p>
                    <div className="flex items-center justify-between">
                        <div className="text-2xl font-bold text-slate-100">{stats.suitExpiredMonth}</div>
                        <span className="text-xs px-2 py-1 rounded bg-slate-800 text-slate-400">Expiring soon</span>
                    </div>
                </div>
                <div className="glass p-5 rounded-xl border border-white/5 hover:border-white/10 transition-colors">
                    <p className="text-sm text-slate-400 mb-1">ID Card Expirations</p>
                    <div className="flex items-center justify-between">
                        <div className="text-2xl font-bold text-slate-100">{stats.cardExpiredMonth}</div>
                        <span className="text-xs px-2 py-1 rounded bg-slate-800 text-slate-400">Expiring soon</span>
                    </div>
                </div>
                <div className="glass p-5 rounded-xl border border-white/5 hover:border-white/10 transition-colors">
                    <p className="text-sm text-slate-400 mb-1">KYC Updates Due</p>
                    <div className="flex items-center justify-between">
                        <div className="text-2xl font-bold text-slate-100">{stats.kycExpiredMonth}</div>
                        <span className="text-xs px-2 py-1 rounded bg-slate-800 text-slate-400">Pending review</span>
                    </div>
                </div>
            </div>
        </div>

        {/* Activity Lists */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="glass rounded-2xl border border-white/5 overflow-hidden">
                <div className="px-6 py-4 border-b border-white/10 flex justify-between items-center bg-white/5">
                    <h3 className="font-semibold">Recently Joined</h3>
                    <Button variant="ghost" size="sm" onClick={() => router.push('/operator/customers')}>View all</Button>
                </div>
                <div className="divide-y divide-white/5">
                    {data.newCustomers && data.newCustomers.length === 0 ? (
                        <div className="p-8 text-center text-slate-500 italic">No new customers today</div>
                    ) : (
                        data.newCustomers?.map(inv => (
                            <div key={inv.custCode} className="px-6 py-4 flex items-center justify-between group hover:bg-white/5 transition-colors">
                                <div className="flex items-center gap-3">
                                    <div className="w-8 h-8 rounded-full bg-blue-500/10 text-blue-400 flex items-center justify-center text-xs">
                                        <Users size={16} />
                                    </div>
                                    <div>
                                        <p className="text-sm font-medium">{inv.fullNameTh}</p>
                                        <p className="text-xs text-slate-500">{inv.custCode}</p>
                                    </div>
                                </div>
                                <Button variant="ghost" size="icon" onClick={() => router.push(`/operator/investor/${inv.custCode}`)}>
                                    <ChevronRight size={16} className="text-slate-500 group-hover:text-white transition-colors" />
                                </Button>
                            </div>
                        ))
                    )}
                </div>
            </div>

            <div className="glass rounded-2xl border border-white/5 overflow-hidden">
                <div className="px-6 py-4 border-b border-white/10 flex justify-between items-center bg-white/5">
                    <h3 className="font-semibold">Profile Updates</h3>
                    <Button variant="ghost" size="sm" onClick={() => router.push('/operator/customers')}>View all</Button>
                </div>
                <div className="divide-y divide-white/5">
                     {data.modifiedCustomers && data.modifiedCustomers.length === 0 ? (
                        <div className="p-8 text-center text-slate-500 italic">No profile updates today</div>
                    ) : (
                        data.modifiedCustomers?.map(inv => (
                            <div key={inv.custCode} className="px-6 py-4 flex items-center justify-between group hover:bg-white/5 transition-colors">
                                <div className="flex items-center gap-3">
                                    <div className="w-8 h-8 rounded-full bg-amber-500/10 text-amber-400 flex items-center justify-center text-xs">
                                        <UserCheck size={16} />
                                    </div>
                                    <div>
                                        <p className="text-sm font-medium">{inv.fullNameTh}</p>
                                        <p className="text-xs text-slate-500">{inv.custCode}</p>
                                    </div>
                                </div>
                                <Button variant="ghost" size="icon" onClick={() => router.push(`/operator/investor/${inv.custCode}`)}>
                                    <ChevronRight size={16} className="text-slate-500 group-hover:text-white transition-colors" />
                                </Button>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    </div>
  );
}
