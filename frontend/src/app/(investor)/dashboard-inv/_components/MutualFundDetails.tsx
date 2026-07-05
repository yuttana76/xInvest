"use client";

import React, { useState } from 'react';
import { ChevronUp, ChevronDown, ThumbsUp, ThumbsDown, TrendingUp, Newspaper, BarChart3 } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer } from 'recharts';
import { MFDetailsProps, ExtendedBalance } from './types';
import { ProductNewsTab } from '@/components/fund/ProductNewsTab';
import { Balance } from '@/lib/api/investor';

// ─── AI Insight card — matches news-headline card style ───────────────────────
type FundAnalysis = NonNullable<Balance['fund_analysis']>;

function timeAgo(iso: string | null): string {
  if (!iso) return '';
  const rtf = new Intl.RelativeTimeFormat('en', { numeric: 'auto', style: 'short' });
  const sec = Math.round((new Date(iso).getTime() - Date.now()) / 1000);
  const abs = Math.abs(sec);
  if (abs < 60)    return rtf.format(sec, 'second');
  if (abs < 3600)  return rtf.format(Math.round(sec / 60), 'minute');
  if (abs < 86400) return rtf.format(Math.round(sec / 3600), 'hour');
  return rtf.format(Math.round(sec / 86400), 'day');
}

function AiRecommendCard({ analysis }: { analysis: FundAnalysis }) {
  const [expanded, setExpanded] = useState(false);

  const impactCfg: Record<string, { dot: string; label: string; pill: string }> = {
    HIGH: { dot: 'bg-rose-500 dark:bg-rose-400',    label: 'High Impact',   pill: 'text-rose-700 border-rose-400/60 bg-rose-50 dark:text-rose-400 dark:border-rose-500/40 dark:bg-rose-500/10'   },
    MED:  { dot: 'bg-amber-500 dark:bg-amber-400',   label: 'Medium Impact', pill: 'text-amber-700 border-amber-400/60 bg-amber-50 dark:text-amber-400 dark:border-amber-400/40 dark:bg-amber-400/10'  },
    LOW:  { dot: 'bg-emerald-500 dark:bg-emerald-400', label: 'Low Impact',  pill: 'text-emerald-700 border-emerald-400/60 bg-emerald-50 dark:text-emerald-400 dark:border-emerald-400/40 dark:bg-emerald-400/10' },
  };
  const lvl = analysis.sentiment_impact_level ?? null;
  const ic  = lvl ? (impactCfg[lvl] ?? impactCfg['LOW']) : null;

  return (
    <div className="mt-2 rounded-2xl border border-slate-200 dark:border-white/10 bg-white dark:bg-slate-900 shadow-sm dark:shadow-lg overflow-hidden">
      {/* Header */}
      <div className="flex items-center gap-2 px-4 pt-3.5 pb-0">
        {/* Gemini-style 4-pointed sparkle */}
        <svg width="13" height="13" viewBox="0 0 28 28" fill="none" className="text-teal-500 dark:text-teal-400 shrink-0" aria-hidden>
          <path d="M14 0 C14 0 15.5 10 20 14 C15.5 18 14 28 14 28 C14 28 12.5 18 8 14 C12.5 10 14 0 14 0Z" fill="currentColor"/>
          <path d="M0 14 C0 14 10 15.5 14 20 C18 15.5 28 14 28 14 C28 14 18 12.5 14 8 C10 12.5 0 14 0 14Z" fill="currentColor"/>
        </svg>
        <span className="text-[11px] font-bold text-slate-800 dark:text-white tracking-wide">AI Insight</span>
      </div>

      {/* Body */}
      <div className="px-4 pt-2 pb-1">
        {analysis.sentiment_summary ? (
          <>
            <p
              className={`text-[12px] leading-relaxed text-slate-700 dark:text-slate-200 ${
                expanded ? '' : 'line-clamp-2'
              }`}
            >
              {analysis.sentiment_summary}
            </p>
            {analysis.sentiment_summary.length > 120 && (
              <button
                onClick={() => setExpanded(v => !v)}
                className="mt-1 text-[10px] font-semibold text-teal-600 hover:text-teal-500 dark:text-teal-400 dark:hover:text-teal-300 transition-colors"
              >
                {expanded ? 'View less' : 'View more'}
              </button>
            )}
          </>
        ) : (
          <p className="text-[11px] text-slate-400 dark:text-slate-500 italic">No summary available.</p>
        )}
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between px-4 py-2.5 mt-1">
        <span className="text-[10px] text-slate-400 dark:text-slate-500">
          {analysis.updated_at && (
            <span>Updated {timeAgo(analysis.updated_at)} · </span>
          )}
          Powered by {APP_NAME}
        </span>
        {/* {ic && (
          <span className={`flex items-center gap-1.5 text-[9px] font-bold uppercase tracking-wider border rounded-full px-2.5 py-0.5 ${ic.pill}`}>
            <span className={`w-1.5 h-1.5 rounded-full ${ic.dot} shrink-0`} />
            {ic.label}
          </span>
        )} */}
      </div>
    </div>
  );
}

export default function MutualFundDetails({
  balances,
  itemColor,
  innerSelectedAccount,
  setInnerSelectedAccount,
  accountIds,
  performanceData,
  perfLoading,
  period,
  setPeriod,
  holdingKeyPrefix,
  expandedHoldings,
  toggleExpand,
  hoveredSentimentKey,
  setHoveredSentimentKey,
}: MFDetailsProps) {
  const [activeTab, setActiveTab] = useState<'info' | 'news'>('info');
  
  const filteredBalances = React.useMemo(() => {
    return innerSelectedAccount === 'all' 
      ? balances 
      : balances.filter((b: ExtendedBalance) => {
          const accId = typeof b.accountID === 'object' ? (b.accountID as { accountID?: string }).accountID || String(b.accountID) : String(b.accountID);
          return accId === innerSelectedAccount;
        });
  }, [balances, innerSelectedAccount]);

  const totalValue = filteredBalances.reduce((sum, b) => sum + (b.unitBalance * b.NAV), 0);
  const totalCost = filteredBalances.reduce((sum, b) => sum + (b.unitBalance * b.averageCost), 0);
  const totalProfit = totalValue - totalCost;
  const totalProfitPercent = totalCost > 0 ? (totalProfit / totalCost) * 100 : 0;

  return (
    <div className="bg-slate-50/50 dark:bg-black/20 rounded-2xl border border-slate-200 dark:border-white/5 p-6 space-y-8 animate-in fade-in duration-300">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 dark:border-white/10 pb-4">
        <div className="flex items-center gap-3">
          <div className="w-4 h-4 rounded-full min-w-4" style={{ backgroundColor: itemColor }} />
          <h3 className="text-xl font-bold text-slate-800 dark:text-slate-100">MF Details</h3>
        </div>
        <div className="flex items-center gap-4 ml-auto text-right flex-wrap sm:flex-nowrap justify-end">
          {accountIds.length > 0 && (
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-500 dark:text-slate-400">Account:</span>
              <select 
                className="bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-lg px-2 py-1 text-xs outline-none text-slate-800 dark:text-slate-100 max-w-[120px] text-ellipsis"
                value={innerSelectedAccount}
                onChange={(e) => setInnerSelectedAccount(e.target.value)}
              >
                <option value="all" className="bg-white dark:bg-slate-800 text-slate-900 dark:text-white">All</option>
                {accountIds.map(acc => (
                  <option key={String(acc)} value={String(acc)} className="bg-white dark:bg-slate-800 text-slate-900 dark:text-white">{String(acc)}</option>
                ))}
              </select>
            </div>
          )}
          <div className="flex flex-col items-end gap-1">
            <p className="text-sm font-medium text-slate-500 dark:text-slate-400">
              Total Balance: <span className="text-slate-800 dark:text-slate-100">{new Intl.NumberFormat('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(totalValue)}</span>
            </p>
            <p className="text-xs font-medium text-slate-500 dark:text-slate-400">
              Profit: <span className={totalProfit >= 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-500'}>
                {totalProfit >= 0 ? '+' : ''}{new Intl.NumberFormat('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(totalProfit)}
                </span>
            </p>
            <p className="text-xs font-medium text-slate-500 dark:text-slate-400">
                <span className={totalProfit >= 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-500'}>
                {totalProfitPercent.toFixed(2)}%
              </span>
            </p>
          </div>
        </div>
      </div>

      {/* Tab Switcher */}
      <div className="flex gap-2 p-1 bg-slate-100 dark:bg-white/5 rounded-xl border border-slate-200 dark:border-white/10 w-fit">
        <button 
          onClick={() => setActiveTab('info')}
          className={`px-4 py-2 rounded-lg text-xs font-bold transition-all flex items-center gap-2 ${activeTab === 'info' ? 'bg-primary text-white shadow-lg' : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200'}`}
        >
          <BarChart3 size={14} />
          PORTFOLIO INFO
        </button>
        <button 
          onClick={() => setActiveTab('news')}
          className={`px-4 py-2 rounded-lg text-xs font-bold transition-all flex items-center gap-2 ${activeTab === 'news' ? 'bg-primary text-white shadow-lg' : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200'}`}
        >
          <Newspaper size={14} />
          NEWS
        </button>
      </div>

      {activeTab === 'info' ? (
        <>
          <div className="w-full">
        <div className="flex items-center justify-between mb-4">
          <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-200">Portfolio Performance</h4>
          <div className="flex bg-slate-100 dark:bg-white/5 p-1 rounded-lg border border-slate-200 dark:border-white/10">
            {[
              { label: '1M', days: 30 },
              { label: '3M', days: 90 },
              { label: '1Y', days: 365 }
            ].map((p) => (
              <button
                key={p.label}
                onClick={() => setPeriod(p.days)}
                className={`px-3 py-1 text-[10px] font-medium rounded-md transition-all ${
                  period === p.days 
                    ? 'bg-primary text-white shadow-lg' 
                    : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-100'
                }`}
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>
        <div className="h-64 w-full relative">
          {perfLoading && (
            <div className="absolute inset-0 flex items-center justify-center bg-black/20 backdrop-blur-[2px] z-10 rounded-xl">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          )}
          {!perfLoading && performanceData.length === 0 && (
            <div className="absolute inset-0 flex items-center justify-center text-slate-400 dark:text-slate-500 text-xs italic">
              {innerSelectedAccount === 'all' 
                ? 'Select an account to view performance' 
                : 'No history data for this period'}
            </div>
          )}
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={performanceData.length > 0 ? performanceData : []}>
              <defs>
                <linearGradient id="colorValueMF" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={itemColor} stopOpacity={0.3}/>
                  <stop offset="95%" stopColor={itemColor} stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" className="dark:stroke-white/10" vertical={false} />
              <XAxis 
                dataKey="date" 
                stroke="#94a3b8" 
                fontSize={10} 
                tickLine={false} 
                axisLine={false}
                minTickGap={30}
                interval="preserveStartEnd"
                tickFormatter={(val) => {
                    if (!val) return '';
                    const d = new Date(val);
                    return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short' });
                }} 
              />
              <YAxis 
                stroke="#94a3b8" 
                fontSize={10} 
                tickLine={false} 
                axisLine={false} 
                width={75}
                domain={['auto', 'auto']}
                padding={{ top: 30 }}
                tickFormatter={(value) => new Intl.NumberFormat('en-US', { 
                    notation: 'compact', 
                    maximumFractionDigits: 1 
                }).format(value)} 
              />
              <RechartsTooltip 
                contentStyle={{ backgroundColor: 'var(--card)', border: '1px solid var(--border)', borderRadius: '12px' }}
                itemStyle={{ color: itemColor }}
                labelFormatter={(label) => new Date(label).toDateString()}
                formatter={(value: number) => [
                    new Intl.NumberFormat('en-US', { minimumFractionDigits: 2 }).format(value),
                    'Market Value'
                ]}
              />
              <Area type="monotone" dataKey="total_market_value" stroke={itemColor} strokeWidth={2} fillOpacity={1} fill="url(#colorValueMF)" animationDuration={1000} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="space-y-4">
        <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-200">Holdings ({filteredBalances.length})</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 items-start">
          {filteredBalances.map((b, bIdx) => {
            const profit = (b.unitBalance * b.NAV) - (b.unitBalance * b.averageCost);
            const profitPercent = (b.unitBalance * b.averageCost) > 0 ? (profit / (b.unitBalance * b.averageCost)) * 100 : 0;
            const holdingKey = `${holdingKeyPrefix}-${bIdx}`;
            const isExpanded = expandedHoldings[holdingKey];

            return (
              <div key={bIdx} className="bg-slate-50 dark:bg-white/5 p-4 rounded-xl border border-slate-100 dark:border-white/5 flex flex-col gap-2 hover:bg-slate-100 dark:hover:bg-white/10 transition-all relative">
                <div className="absolute top-0 left-0 w-1 h-full rounded-l-xl" style={{ backgroundColor: itemColor }} />
                <div 
                  className="flex items-start justify-between border-b border-slate-200 dark:border-white/10 pb-2 mb-1 pl-2 cursor-pointer"
                  onClick={() => toggleExpand(holdingKey)}
                >
                  <div className="flex-1 min-w-0">
                    <div 
                      className="flex items-center gap-2 relative"
                      onMouseEnter={() => setHoveredSentimentKey(holdingKey)}
                      onMouseLeave={() => setHoveredSentimentKey(null)}
                    >
                      <div className="text-sm font-bold text-slate-800 dark:text-slate-200 truncate pr-2" title={b.fundCode}>
                        {b.fundCode}
                      </div>

                      {b.fund_analysis?.sentiment_score !== undefined && b.fund_analysis?.sentiment_score !== null && (
                        <div className="flex items-center cursor-help transition-transform hover:scale-110 p-1">
                          {b.fund_analysis.sentiment_score > 0 ? (
                            <span className="text-emerald-300 font-bold text-lg leading-none" role="img" aria-label="bull"><ThumbsUp size={18} /></span>
                          ) : b.fund_analysis.sentiment_score < 0 ? (
                            <span className="text-rose-300 font-bold text-lg leading-none" role="img" aria-label="bear"><ThumbsDown size={18} /></span>
                          ) : null}
                        </div>
                      )}

                      {hoveredSentimentKey === holdingKey && b.fund_analysis && (
                        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-3 w-64 z-50 animate-in fade-in zoom-in-95 duration-200 pointer-events-none">
                          <div className="backdrop-blur-xl border border-slate-200 dark:border-white/10 p-4 rounded-2xl shadow-2xl relative bg-white/95 dark:bg-slate-900/90">
                            <div className="absolute -bottom-1.5 left-1/2 -translate-x-1/2 w-3 h-3 bg-white dark:bg-slate-900 border-r border-b border-slate-200 dark:border-white/10 rotate-45" />
                            <div className="flex items-center gap-2 mb-2 pb-2 border-b border-slate-100 dark:border-white/5">
                              <TrendingUp size={14} className="text-primary" />
                              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Market Sentiment</span>
                            </div>
                            <p className="text-xs text-slate-700 dark:text-slate-200 leading-relaxed italic">
                              &ldquo;{b.fund_analysis.sentiment_summary || `Sentiment Score: ${b.fund_analysis.sentiment_score}`}&rdquo;
                            </p>
                            <p className="text-xs text-slate-400 mt-2 font-medium opacity-60">
                              see more in news.
                            </p>
                          </div>
                        </div>
                      )}

                      <div className="text-slate-400">
                        {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                      </div>
                    </div>
                    <div className="text-[10px] text-slate-500 mt-0.5 font-medium">
                      {typeof b.accountID === 'object' ? (b.accountID as { accountID?: string }).accountID || String(b.accountID) : String(b.accountID)}
                    </div>
                  </div>
                  
                  <div className="text-right shrink-0">
                    <div className="flex flex-col">
                      <div className="text-xs text-slate-500 dark:text-slate-400">
                        Amount <span className="text-slate-800 dark:text-slate-100 font-bold ml-1">{new Intl.NumberFormat('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(b.amount)}</span>
                      </div>
                      <div className="flex items-center justify-end gap-2">
                        <div className={`text-xs font-bold ${profit >= 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-500'}`}>
                          {profit >= 0 ? '+' : ''}{new Intl.NumberFormat('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(profit)}
                        </div>
                        <div className={`text-[10px] font-medium ${profit >= 0 ? 'text-emerald-600/80 dark:text-emerald-400/80' : 'text-rose-600/80 dark:text-rose-500/80'}`}>
                          {profitPercent.toFixed(2)}%
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {isExpanded && (
                  <div className="animate-in slide-in-from-top-1 duration-200 space-y-4">
                    {/* Fund Stats Grid */}
                    <div className="grid grid-cols-2 gap-y-3 gap-x-4 text-xs pl-2 pt-2">
                      <div className="text-slate-500 dark:text-slate-400">Unit Balance: <span className="text-slate-800 dark:text-slate-100 block font-medium mt-0.5">{Number(b.unitBalance).toLocaleString(undefined, { minimumFractionDigits: 4, maximumFractionDigits: 4 })}</span></div>
                      <div className="text-slate-500 dark:text-slate-400">Average Cost: <span className="text-slate-800 dark:text-slate-100 block font-medium mt-0.5">{Number(b.averageCost).toFixed(4)}</span></div>
                      <div className="text-slate-500 dark:text-slate-400">NAV: <span className="text-slate-800 dark:text-slate-100 block font-medium mt-0.5">{Number(b.NAV).toFixed(4)}</span></div>
                      <div className="text-slate-500 dark:text-slate-400">NAV Date: <span className="text-slate-800 dark:text-slate-100 block font-medium mt-0.5">{new Date(b.NAVdate).toLocaleDateString('en-GB')}</span></div>
                    </div>

                    {/* AI Recommendation Panel — news card style */}
                    {b.fund_analysis && (b.fund_analysis.sentiment_summary || b.fund_analysis.sentiment_impact_level) && (
                      <AiRecommendCard analysis={b.fund_analysis} />
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
        </>
      ) : (
        <div className="pt-4 border-t border-slate-200 dark:border-white/5">
          <ProductNewsTab productType="mf" />
        </div>
      )}
    </div>
  );
}
