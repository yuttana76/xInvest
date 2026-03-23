"use client";

import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip as RechartsTooltip } from 'recharts';
import { AssetAllocationItem } from './types';
import { PerformanceChartData } from '@/lib/api/investor';
import MutualFundDetails from './MutualFundDetails';
import PrivateFundDetails from './PrivateFundDetails';
import BondDetails from './BondDetails';

interface AssetAllocationProps {
  allocationData: AssetAllocationItem[];
  expandedFund: string | null;
  setExpandedFund: (fund: string | null) => void;
  innerSelectedAccount: string;
  setInnerSelectedAccount: (accountId: string) => void;
  performanceData: PerformanceChartData[];
  perfLoading: boolean;
  period: number;
  setPeriod: (days: number) => void;
  hoveredSentimentKey: string | null;
  setHoveredSentimentKey: (key: string | null) => void;
  expandedHoldings: Record<string, boolean>;
  toggleExpand: (holdingKey: string) => void;
}

const COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

export default function AssetAllocation({
  allocationData,
  expandedFund,
  setExpandedFund,
  innerSelectedAccount,
  setInnerSelectedAccount,
  performanceData,
  perfLoading,
  period,
  setPeriod,
  hoveredSentimentKey,
  setHoveredSentimentKey,
  expandedHoldings,
  toggleExpand,
}: AssetAllocationProps) {
  
  const currentFundName = expandedFund || (allocationData.length > 0 ? allocationData[0].name : null);

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
        <span className="w-1 h-6 bg-primary rounded-full"></span>
        Asset Allocation
      </h2>

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 items-start">
        {/* Left Column: Pie Chart and Legend */}
        <div className="xl:col-span-4 glass p-8 rounded-2xl border border-white/5 h-full">
          <div className="h-64 w-full relative">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={allocationData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                  stroke="none"
                  onClick={(data) => setExpandedFund(data.name)}
                >
                  {allocationData.map((entry, index) => (
                    <Cell 
                        key={`cell-${index}`} 
                        fill={COLORS[index % COLORS.length]} 
                        className={`cursor-pointer transition-all duration-300 hover:opacity-80 ${currentFundName === entry.name ? 'stroke-white stroke-2' : ''}`}
                    />
                  ))}
                </Pie>
                <RechartsTooltip 
                  contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px' }}
                  itemStyle={{ color: '#f1f5f9' }}
                  formatter={(value: number) => [`$${new Intl.NumberFormat('en-US').format(value)}`, 'Value']}
                />
              </PieChart>
            </ResponsiveContainer>
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-center">
              <p className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">Total</p>
              <p className="text-lg font-bold text-slate-100">
                ${new Intl.NumberFormat('en-US', { notation: 'compact' }).format(allocationData.reduce((a, b) => a + b.value, 0))}
              </p>
            </div>
          </div>

          <div className="mt-8 space-y-3">
            {allocationData.map((item, index) => (
              <button
                key={index}
                onClick={() => setExpandedFund(item.name)}
                className={`w-full flex items-center justify-between p-3 rounded-xl transition-all border ${
                    currentFundName === item.name 
                    ? 'bg-primary/20 border-primary/30 shadow-[0_0_20px_rgba(99,102,241,0.15)]' 
                    : 'bg-white/5 border-transparent hover:bg-white/10'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS[index % COLORS.length] }} />
                  <span className="text-sm font-medium text-slate-200">{item.name}</span>
                </div>
                <div className="text-right">
                  <span className="text-sm font-bold text-slate-100">{item.percent.toFixed(1)}%</span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Right Column: Details of Selected Product */}
        <div className="xl:col-span-8 h-full">
          {allocationData
            .filter(item => item.name === currentFundName)
            .map((item, i) => {
              const itemColor = COLORS[allocationData.indexOf(item) % COLORS.length];
              const uniqueAccountIds: string[] = Array.from(new Set(item.balances.map(b => String(b.accountID))));

              return (
                <div key={i} className="h-full">
                  {item.name === 'MF' && (
                    <MutualFundDetails
                       balances={item.balances}
                       itemColor={itemColor}
                       innerSelectedAccount={innerSelectedAccount}
                       setInnerSelectedAccount={setInnerSelectedAccount}
                       accountIds={uniqueAccountIds}
                       performanceData={performanceData}
                       perfLoading={perfLoading}
                       period={period}
                       setPeriod={setPeriod}
                       holdingKeyPrefix="MF"
                       expandedHoldings={expandedHoldings}
                       toggleExpand={toggleExpand}
                       hoveredSentimentKey={hoveredSentimentKey}
                       setHoveredSentimentKey={setHoveredSentimentKey}
                    />
                  )}
                  {item.name === 'PF' && (
                    <PrivateFundDetails
                       balances={item.balances}
                       itemColor={itemColor}
                       innerSelectedAccount={innerSelectedAccount}
                       setInnerSelectedAccount={setInnerSelectedAccount}
                       accountIds={uniqueAccountIds}
                       performanceData={performanceData}
                       perfLoading={perfLoading}
                       period={period}
                       setPeriod={setPeriod}
                       holdingKeyPrefix="PF"
                       expandedHoldings={expandedHoldings}
                       toggleExpand={toggleExpand}
                    />
                  )}
                  {item.name === 'Bond' && (
                    <BondDetails
                       balances={item.balances}
                       itemColor={itemColor}
                       expandedHoldings={expandedHoldings}
                       toggleExpand={toggleExpand}
                    />
                  )}
                </div>
              );
            })}
        </div>
      </div>
    </div>
  );
}
