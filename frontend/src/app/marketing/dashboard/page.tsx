'use client';

import React, { useEffect, useState } from 'react';
import { Users, Wallet, TrendingUp, PieChart as PieChartIcon, Activity } from 'lucide-react';
import { getMarketingDashboardStats, type MarketingDashboardStats } from '@/lib/api/investor';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#8b5cf6', '#ec4899', '#06b6d4'];

export default function MarketingDashboard() {
  const [data, setData] = useState<MarketingDashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchRef = React.useRef(false);

  useEffect(() => {
    if (fetchRef.current) return;
    fetchRef.current = true;
    getMarketingDashboardStats().then(setData).finally(() => setLoading(false));
  }, []);

  if (loading || !data) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  const { stats, statusDistribution, profile } = data;
  
  const pieData = Object.entries(statusDistribution).map(([name, value]) => ({ name, value }));
  const aumDistribution = [
    { name: 'Mutual Funds', value: stats.mfAUM, color: COLORS[0] },
    { name: 'Bonds', value: stats.bondAUM, color: COLORS[1] },
    { name: 'Private Funds', value: stats.pfAUM, color: COLORS[2] },
  ].filter(d => d.value > 0);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Marketing Portal</h1>
        <p className="text-slate-400 mt-1">Hello {profile.fullName}, here&apos;s your performance overview.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {[
          { label: "Total AUM", value: `$${stats.totalAUM.toLocaleString()}`, icon: <Wallet size={20} />, color: "emerald" },
          { label: "Total Investors", value: stats.totalInvestors, icon: <Users size={20} />, color: "blue" },
        ].map((stat, i) => (
          <div key={i} className="glass p-6 rounded-2xl border border-white/5">
            <div className={`p-2 bg-${stat.color}-500/10 text-${stat.color}-400 rounded-lg w-fit mb-4`}>
                {stat.icon}
            </div>
            <p className="text-sm text-slate-400">{stat.label}</p>
            <h3 className="text-2xl font-bold mt-1">{stat.value}</h3>
          </div>
        ))}
      </div>

      {/* Product Portfolio Breakdown */}
      <div>
        <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
          <PieChartIcon size={20} className="text-primary" />
          Product Portfolio
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            { 
              name: 'Mutual Funds', 
              aum: stats.mfAUM, 
              sub: stats.mfSubThisMonth,
              color: '#10b981', 
              icon: <Wallet size={18} />,
              description: 'Diversified portfolios'
            },
            { 
              name: 'Bonds', 
              aum: stats.bondAUM, 
              sub: stats.bondSubThisMonth,
              color: '#3b82f6', 
              icon: <Activity size={18} />,
              description: 'Fixed income assets'
            },
            { 
              name: 'Private Funds', 
              aum: stats.pfAUM, 
              sub: stats.pfSubThisMonth,
              color: '#f59e0b', 
              icon: <TrendingUp size={18} />,
              description: 'Exclusive investments'
            },
          ].map((product, i) => {
            const percentage = stats.totalAUM > 0 ? (product.aum / stats.totalAUM * 100).toFixed(1) : '0';
            return (
              <div key={i} className="glass p-6 rounded-2xl border border-white/5 relative overflow-hidden group">
                <div className="absolute top-0 left-0 w-1 h-full" style={{ backgroundColor: product.color }} />
                <div className="flex justify-between items-start mb-4">
                  <div className="p-2 rounded-lg bg-white/5 text-slate-100 opacity-80 group-hover:opacity-100 transition-opacity">
                    {product.icon}
                  </div>
                  <span className="text-[10px] font-bold px-2 py-1 rounded bg-white/5 text-slate-400">
                    {percentage}% Share
                  </span>
                </div>
                <div>
                  <h4 className="text-slate-400 text-sm font-medium">{product.name}</h4>
                  <p className="text-2xl font-bold text-slate-100 mt-1">${product.aum.toLocaleString()}</p>
                  
                  <div className="mt-4 flex items-center justify-between">
                    <div>
                      <p className="text-[10px] text-slate-500 uppercase tracking-wider">SUB this month</p>
                      <p className="text-sm font-semibold text-emerald-400">+${product.sub.toLocaleString()}</p>
                    </div>
                    <p className="text-xs text-slate-500 self-end mb-0.5">{product.description}</p>
                  </div>
                </div>
                <div className="mt-4 h-1.5 bg-white/5 rounded-full overflow-hidden">
                  <div 
                    className="h-full transition-all duration-1000" 
                    style={{ backgroundColor: product.color, width: `${percentage}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Asset Distribution Chart */}
        <div className="glass p-8 rounded-2xl border border-white/5">
          <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
            <PieChartIcon size={20} className="text-primary" />
            Asset Distribution
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={aumDistribution}
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {aumDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-3 gap-4 mt-4">
            {aumDistribution.map((d, i) => (
                <div key={i} className="text-center">
                    <p className="text-xs text-slate-500 mb-1">{d.name}</p>
                    <p className="text-sm font-bold text-slate-200">${d.value.toLocaleString()}</p>
                </div>
            ))}
          </div>
        </div>

        {/* Onboarding Funnel / Status */}
        <div className="glass p-8 rounded-2xl border border-white/5">
          <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
            <Activity size={20} className="text-primary" />
            Investor Status Summary
          </h3>
          <div className="space-y-4">
            {pieData.map((item, i) => {
                const percent = (item.value / (stats.totalInvestors || 1) * 100).toFixed(0);
                return (
                    <div key={i}>
                        <div className="flex justify-between text-sm mb-2">
                            <span className="text-slate-300 font-medium">{item.name}</span>
                            <span className="text-slate-400">{item.value} ({percent}%)</span>
                        </div>
                        <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                            <div 
                                className="h-full bg-primary" 
                                style={{ width: `${percent}%` }}
                            />
                        </div>
                    </div>
                );
            })}
            {pieData.length === 0 && (
                <div className="text-center py-12 text-slate-500 italic">
                    No status data available
                </div>
            )}
          </div>
        </div>
      </div>

      {/* Compliance Section moved to Bottom */}
      <div className="glass p-6 rounded-2xl border border-white/5">
        <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
          <Activity size={20} className="text-rose-400" />
          Attention Required (This Month Expirations)
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="flex items-center gap-4 p-4 rounded-xl bg-slate-800/50 border border-white/5">
            <div className="p-3 bg-rose-500/10 text-rose-400 rounded-lg">
              <Activity size={20} />
            </div>
            <div>
              <p className="text-sm text-slate-400">KYC Expiry</p>
              <p className="text-xl font-bold text-rose-400">{data.alerts.kyc}</p>
            </div>
          </div>
          <div className="flex items-center gap-4 p-4 rounded-xl bg-slate-800/50 border border-white/5">
            <div className="p-3 bg-rose-500/10 text-rose-400 rounded-lg">
              <Activity size={20} />
            </div>
            <div>
              <p className="text-sm text-slate-400">Card Expiry</p>
              <p className="text-xl font-bold text-rose-400">{data.alerts.card}</p>
            </div>
          </div>
          <div className="flex items-center gap-4 p-4 rounded-xl bg-slate-800/50 border border-white/5">
            <div className="p-3 bg-rose-500/10 text-rose-400 rounded-lg">
              <Activity size={20} />
            </div>
            <div>
              <p className="text-sm text-slate-400">Suitability Expiry</p>
              <p className="text-xl font-bold text-rose-400">{data.alerts.suitability}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
