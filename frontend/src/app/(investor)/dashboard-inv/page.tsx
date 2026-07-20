"use client";

import React, { useEffect, useState, useMemo, useRef } from 'react';
import { getInvestorDashboardData, getMFPerformanceData, getPFPerformanceData, type InvestorData, type PerformanceChartData } from '@/lib/api/investor';
import PortfolioStats from './_components/PortfolioStats';
import AssetAllocation from './_components/AssetAllocation';

const COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

export default function Dashboard() {
  const [data, setData] = useState<InvestorData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedFund, setExpandedFund] = useState<string | null>(null);
  const [innerSelectedAccount, setInnerSelectedAccount] = useState<string>('all');
  const [performanceData, setPerformanceData] = useState<PerformanceChartData[]>([]);
  const [perfLoading, setPerfLoading] = useState(false);
  const [period, setPeriod] = useState<number>(30); // Default 1M (30 days)
  const [expandedHoldings, setExpandedHoldings] = useState<Record<string, boolean>>({});
  const [hoveredSentimentKey, setHoveredSentimentKey] = useState<string | null>(null);

  useEffect(() => {
    setInnerSelectedAccount('all');
  }, [expandedFund]);

  const fetchRef = useRef(false);

  useEffect(() => {
    if (fetchRef.current) return;
    fetchRef.current = true;
    
    const fetchDashboardData = async () => {
      try {
        const dashboardData = await getInvestorDashboardData();
        setData(dashboardData);
      } catch (err: unknown) {
        // @ts-expect-error - error structure depends on api response
        setError(err?.response?.data?.error || 'Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const allBalances = useMemo(() => {
    if (!data) return [];
    
    const mfBals = (data.mfAccounts || []).flatMap(acc => (acc.balances || []).map(b => ({...b, group: 'MF', status: undefined as string | undefined, fromDate: undefined as string | undefined})));
    const pfBals = (data.privateFundAccounts || []).flatMap(acc => (acc.privateFundBalances || []).map(b => ({...b, group: 'PF', status: undefined as string | undefined, fromDate: undefined as string | undefined})));
    const bondBals = (data.bondAccounts || []).map((b, i) => ({
      accountID: b.compCode || `bond-${i}`,
      fundCode: b.bondCode || `Bond (${b.compCode || 'Unknown'})`,
      amount: Number(b.amount || 0),
      averageCost: Number(b.amount || 0),
      NAV: Number(b.amount || 0),
      unitBalance: 1,
      NAVdate: b.fromDate || new Date().toISOString(),
      status: b.status,
      fromDate: b.fromDate,
      toDate: b.toDate,
      group: 'Bond'
    }));
    
    return [...mfBals, ...pfBals, ...bondBals];
  }, [data]);

  const stats = useMemo(() => {
    if (!data) return { totalBalance: 0, netProfit: 0, profitPercent: 0 };
    
    let totalValue = 0;
    let totalCost = 0;

    allBalances.forEach(b => {
      const isBond = b.group === 'Bond';
      const isActiveBond = isBond ? b.status?.toLowerCase() === 'active' : true;

      // Only add to summary stats if it's active (or not a bond)
      if (isActiveBond) {
        const currentValue = b.unitBalance * b.NAV;
        const cost = b.unitBalance * b.averageCost;
        totalValue += currentValue;
        totalCost += cost;
      }
    });

    const netProfit = totalValue - totalCost;
    const profitPercent = totalCost > 0 ? (netProfit / totalCost) * 100 : 0;

    return { totalBalance: totalValue, netProfit, profitPercent };
  }, [allBalances, data]);

  const allocationData = useMemo(() => {
    if (allBalances.length === 0) return [];
    
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const groupStats: Record<string, { value: number, cost: number, balances: any[] }> = {};
    let grandTotal = 0;

    allBalances.forEach(b => {
      const isBond = b.group === 'Bond';
      const isActiveBond = isBond ? b.status?.toLowerCase() === 'active' : true;

      const val = isActiveBond ? b.unitBalance * b.NAV : 0;
      const cost = isActiveBond ? b.unitBalance * b.averageCost : 0;
      const group = b.group;

      if (!groupStats[group]) {
        groupStats[group] = { value: 0, cost: 0, balances: [] };
      }
      groupStats[group].value += val;
      groupStats[group].cost += cost;
      groupStats[group].balances.push(b);
      grandTotal += val;
    });

    return Object.entries(groupStats).map(([name, groupStats], idx) => {
      const netProfit = groupStats.value - groupStats.cost;
      const profitPercent = groupStats.cost > 0 ? (netProfit / groupStats.cost) * 100 : 0;
      return {
        name,
        percent: grandTotal > 0 ? (groupStats.value / grandTotal) * 100 : 0,
        value: groupStats.value,
        profit: netProfit,
        profitPercent,
        balances: groupStats.balances,
        color: COLORS[idx % COLORS.length]
      };
    }).sort((a, b) => b.value - a.value);
  }, [allBalances]);

  // Initialize expandedFund with the first fund type if not set
  useEffect(() => {
    if (data && !expandedFund && allocationData.length > 0) {
      setExpandedFund(allocationData[0].name);
    }
  }, [data, allocationData, expandedFund]);

  // Fetch performance data when account or period changes
  useEffect(() => {
    if (!expandedFund) return;

    const fetchPerformance = async () => {
      setPerfLoading(true);
      try {
        let result;
        if (expandedFund === 'MF') {
          result = await getMFPerformanceData(innerSelectedAccount, period);
        } else if (expandedFund === 'PF') {
          result = await getPFPerformanceData(innerSelectedAccount, period);
        }
        
        if (result && result.chart_data) {
          setPerformanceData(result.chart_data);
        } else {
          setPerformanceData([]);
        }
      } catch (err) {
        console.error('Failed to fetch performance data:', err);
        setPerformanceData([]);
      } finally {
        setPerfLoading(false);
      }
    };

    fetchPerformance();
  }, [innerSelectedAccount, expandedFund, period]);

  const toggleExpand = (holdingKey: string) => {
    setExpandedHoldings(prev => ({
      ...prev,
      [holdingKey]: !prev[holdingKey]
    }));
  };

  if (loading) {
    return <div className="flex h-96 items-center justify-center text-slate-500 dark:text-slate-400">Loading dashboard...</div>;
  }

  if (error) {
    return <div className="flex h-96 items-center justify-center text-rose-500">{error}</div>;
  }

  const { profile } = data || {};

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight bg-linear-to-r from-slate-900 via-slate-700 to-slate-500 dark:from-white dark:to-slate-400 bg-clip-text text-transparent">Portfolio Overview</h1>
          <p className="text-slate-600 dark:text-slate-400 mt-1">Welcome {profile?.fullNameEn || profile?.fullNameTh}, view your portfolio performance here.</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="px-4 py-2 bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded-xl backdrop-blur-md">
            <span className="text-sm text-slate-600 dark:text-slate-400 mr-2">Market Status:</span>
            <span className="text-sm font-medium text-emerald-600 dark:text-emerald-400 flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              Open
            </span>
          </div>
        </div>
      </div>

      <PortfolioStats stats={stats} />

      <AssetAllocation 
        allocationData={allocationData}
        expandedFund={expandedFund}
        setExpandedFund={setExpandedFund}
        innerSelectedAccount={innerSelectedAccount}
        setInnerSelectedAccount={setInnerSelectedAccount}
        performanceData={performanceData}
        perfLoading={perfLoading}
        period={period}
        setPeriod={setPeriod}
        hoveredSentimentKey={hoveredSentimentKey}
        setHoveredSentimentKey={setHoveredSentimentKey}
        expandedHoldings={expandedHoldings}
        toggleExpand={toggleExpand}
      />
    </div>
  );
}
