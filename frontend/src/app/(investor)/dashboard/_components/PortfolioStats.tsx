"use client";

import React from 'react';
import { Wallet, TrendingUp, ArrowUpRight, ArrowDownRight } from 'lucide-react';

interface PortfolioStatsProps {
  stats: {
    totalBalance: number;
    netProfit: number;
    profitPercent: number;
  };
}

export default function PortfolioStats({ stats }: PortfolioStatsProps) {
  const statItems = [
    { 
      label: "Total Balance", 
      value: new Intl.NumberFormat('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(stats.totalBalance), 
      change: "", 
      up: true, 
      icon: <Wallet size={20} /> 
    },
    { 
      label: "Net Profit/Loss", 
      value: new Intl.NumberFormat('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(stats.netProfit), 
      change: `${stats.profitPercent > 0 ? '+' : ''}${stats.profitPercent.toFixed(2)}%`, 
      up: stats.netProfit >= 0, 
      icon: <TrendingUp size={20} /> 
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
      {statItems.map((stat, i) => (
        <div key={i} className="glass p-6 rounded-2xl border border-slate-200/50 dark:border-white/5">
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-primary/10 text-primary rounded-lg">{stat.icon}</div>
            {stat.change && (
              <div className={`flex items-center gap-1 text-xs font-medium ${stat.up ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-500'}`}>
                {stat.up ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
                {stat.change}
              </div>
            )}
          </div>
          <p className="text-sm text-slate-500 dark:text-slate-400">{stat.label}</p>
          <h3 className="text-2xl font-bold mt-1 text-slate-900 dark:text-slate-100">{stat.value}</h3>
        </div>
      ))}
    </div>
  );
}
