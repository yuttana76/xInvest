'use client';

import React, { useState, useMemo } from 'react';
import { useParams } from 'next/navigation';
import { useQuery } from '@apollo/client';
import { GET_FUND_PROFILE_BY_CODE } from '@/lib/graphql/queries';
import { Navbar } from '@/components/Navbar';
import { Title, Text, Metric, AreaChart, DonutChart, List, ListItem, Divider } from '@tremor/react';

// Force Tailwind v4 to compile Tremor dynamic color classes for the DonutChart
export const TREMOR_SAFELIST = [
  'fill-emerald-500', 'bg-emerald-500', 'text-emerald-500',
  'fill-blue-500', 'bg-blue-500', 'text-blue-500',
  'fill-violet-500', 'bg-violet-500', 'text-violet-500',
  'fill-amber-500', 'bg-amber-500', 'text-amber-500',
  'fill-rose-500', 'bg-rose-500', 'text-rose-500',
  'fill-cyan-500', 'bg-cyan-500', 'text-cyan-500',
  'fill-fuchsia-500', 'bg-fuchsia-500', 'text-fuchsia-500'
];

export default function FundDetailPage() {
  const params = useParams();
  const fundCode = decodeURIComponent(params.fundCode as string).toUpperCase();
  const [selectedPeriod, setSelectedPeriod] = useState('1M');

  const { data, loading, error } = useQuery(GET_FUND_PROFILE_BY_CODE, {
    variables: { fundCode },
    skip: !fundCode,
    fetchPolicy: 'network-only', // Ensure we get fresh calculations bypassing Apollo cache
  });

  const profile = data?.fundProfileByCode;

  // Generate realistic mock timeseries ensuring the final datapoint matches the database
  const chartData = useMemo(() => {
    if (!profile) return [];
    const perf = profile.fundPerformance?.[0];
    if (!perf) return [];

    let target = 0;
    let points = 30; // Default size

    const parse = (val: string | number | null | undefined, fallback: number) => {
        if (val === null || val === undefined) return fallback;
        const num = typeof val === 'string' ? parseFloat(val) : val;
        return isNaN(num) ? fallback : num;
    };

    // A simple deterministic pseudo-random generator
    const pseudoRandom = (seed: number) => {
        const x = Math.sin(seed) * 10000;
        return x - Math.floor(x);
    };

    switch (selectedPeriod) {
      case '1D': target = parse(perf.p1mReturn, 1) / 30; points = 24; break;
      case '1W': target = parse(perf.p1wReturn, parse(perf.p1mReturn, 2) / 4); points = 7; break;
      case '1M': target = parse(perf.p1mReturn, 3); points = 30; break;
      case '3M': target = parse(perf.p3mReturn, 5); points = 90; break;
      case '6M': target = parse(perf.p6mReturn, 8); points = 180; break;
      case 'YTD': target = parse(perf.pYtdReturn, 10); points = 120; break;
      case '1Y': target = parse(perf.p1yReturn, 12); points = 12; break;
      case '3Y': target = parse(perf.p3yReturn, 25); points = 36; break;
      case '5Y': target = parse(perf.p5yReturn, 40); points = 60; break;
    }

    const data = [];
    let current = 0;
    const step = target / points;
    const seedBase = perf.p1yReturn ? parse(perf.p1yReturn, 1) : 1;

    for (let i = 0; i < points; i++) {
        if (i === points - 1) {
            data.push({ date: `T-${points - i}`, Return: Number(target.toFixed(2)) });
        } else {
            const noise = (pseudoRandom(seedBase + i) - 0.5) * (Math.abs(target) * 0.1 || 0.5);
            current += step + noise;
            data.push({ date: `T-${points - i}`, Return: Number(current.toFixed(2)) });
        }
    }
    return data;
  }, [profile, selectedPeriod]);

  // Asset Allocation Data Parsing
  const allocationData = useMemo(() => {
    if (!profile?.assetAllocation) return [];
    
    const groups: Record<string, number> = {
      'หุ้น': 0,
      'หุ้นกู้': 0,
      'หน่วยลงทุน': 0,
      'ใบสำคัญแสดงสิทธิ': 0,
      'เงินฝากธนาคาร P/N และ B/E': 0,
      'พันธบัตรรัฐบาลและรัฐวิสาหกิจ': 0,
      'ทองคำแท่ง': 0,
      'ตราสารอนุพันธ์': 0,
      'สินทรัพย์อื่นๆ/หนี้สินอื่นๆ': 0
    };

    let totalFundSize903 = 0;
    const inRange = (c: number, min: number, max: number) => c >= min && c <= max;

    profile.assetAllocation.forEach((item: any) => {
      const code = parseInt(item.investmentTypeCode, 10);
      const size = Number(item.investmentSize);

      if (code === 903) {
          totalFundSize903 = size;
      } else if (inRange(code, 101, 102)) {
         groups['หุ้น'] += size;
      } else if (inRange(code, 103, 107)) {
         groups['หุ้นกู้'] += size;
      } else if (inRange(code, 108, 109) || inRange(code, 117, 121) || code === 139) {
         groups['หน่วยลงทุน'] += size;
      } else if (inRange(code, 110, 116) || inRange(code, 124, 129)) {
         groups['ใบสำคัญแสดงสิทธิ'] += size;
      } else if (inRange(code, 201, 205) || inRange(code, 216, 224)) {
         groups['เงินฝากธนาคาร P/N และ B/E'] += size;
      } else if (inRange(code, 206, 210) || code === 213) {
         groups['พันธบัตรรัฐบาลและรัฐวิสาหกิจ'] += size;
      } else if (code === 450) {
         groups['ทองคำแท่ง'] += size;
      } else if (inRange(code, 401, 407)) {
         groups['ตราสารอนุพันธ์'] += size;
      } else if (
         code === 122 || code === 211 || code === 700 ||
         inRange(code, 301, 399) || inRange(code, 500, 599)
      ) {
         groups['สินทรัพย์อื่นๆ/หนี้สินอื่นๆ'] += size;
      } else if (inRange(code, 601, 699)) {
         groups['สินทรัพย์อื่นๆ/หนี้สินอื่นๆ'] -= Math.abs(size);
      }
    });

    let sumCategorized = 0;
    Object.values(groups).forEach(val => sumCategorized += val);
    
    // Choose denominator
    const denominator = totalFundSize903 > 0 ? totalFundSize903 : (sumCategorized !== 0 ? sumCategorized : 1);

    return Object.keys(groups)
      .map(key => {
         const val = groups[key];
         const percent = (val / denominator) * 100;
         return { name: key, value: percent };
      })
      .filter(item => item.value > 0) // Retain all non-zero
      .sort((a, b) => b.value - a.value);
  }, [profile]);
  
  // Top Holding Data Parsing
  const topHoldingData = useMemo(() => {
    if (!profile?.topHolding) return [];
    
    return profile.topHolding
      .map((item: any) => ({
        name: item.securitiesName,
        value: Number(item.securitiesInvestSize)
      }))
      .sort((a: any, b: any) => b.value - a.value);
  }, [profile]);

  if (loading) {
    return (
      <main className="min-h-screen relative overflow-hidden bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-white flex items-center justify-center transition-colors duration-300">
        <Navbar />
        <Text className="text-xl animate-pulse text-slate-500 dark:text-slate-400">Loading fund details...</Text>
      </main>
    );
  }

  if (error) {
    return (
      <main className="min-h-screen relative overflow-hidden bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-white flex items-center justify-center transition-colors duration-300">
        <Navbar />
        <Text className="text-xl text-red-600 dark:text-red-500">Error loading fund details: {error.message}</Text>
      </main>
    );
  }

  if (!profile) {
    return (
      <main className="min-h-screen relative overflow-hidden bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-white flex items-center justify-center transition-colors duration-300">
        <Navbar />
        <Text className="text-xl text-slate-500 dark:text-slate-400">Fund not found</Text>
      </main>
    );
  }

  // Tonal Layering and No 1px Border Rule (No-Line Rule)
  // Background Shifts to distinguish sections without lines
  // The Power Gradient for the primary buttons

  return (
    <main className="min-h-screen relative overflow-hidden bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-white pb-32 transition-colors duration-300">
      <Navbar />

      {/* Background Decor */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary/20 dark:bg-primary/10 blur-[120px] rounded-full -z-10" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-accent/20 dark:bg-accent/10 blur-[120px] rounded-full -z-10" />

      {/* Hero Section */}
      <section className="pt-32 px-4 max-w-6xl mx-auto">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-12">
          <div>
            <div className="flex items-center gap-3 mb-4">
              <span className="px-3 py-1 bg-black/5 dark:bg-surface-container-low text-slate-600 dark:text-slate-300 text-sm font-medium rounded-full backdrop-blur-md dark:bg-white/5 border border-slate-200 dark:border-transparent">
                {profile.amcCode}
              </span>
              <span className="px-3 py-1 bg-black/5 dark:bg-surface-container-low text-slate-600 dark:text-slate-300 text-sm font-medium rounded-full backdrop-blur-md dark:bg-white/5 border border-slate-200 dark:border-transparent">
                Risk Level: {profile.fundRiskLevel}
              </span>
            </div>
            <Title className="text-5xl md:text-6xl font-bold tracking-tight mb-2 font-display text-slate-900 dark:text-white">
              {profile.fundCode}
            </Title>
            <Text className="text-xl text-slate-600 dark:text-slate-400 max-w-2xl font-inter">
              {profile.fundNameTh}
            </Text>
            <Text className="text-md text-slate-500 mt-1 font-inter">
              {profile.fundNameEn}
            </Text>
          </div>
          
          <div className="flex flex-col items-end">
            <button className="bg-gradient-to-br from-primary to-primary-container text-white px-8 py-3 rounded-lg font-medium shadow-[0_0_40px_rgba(0,59,147,0.3)] hover:shadow-[0_0_60px_rgba(0,59,147,0.5)] transition-all">
              Invest Now
            </button>
            <Text className="text-xs text-slate-500 mt-3">NAV Date: {profile.fundPerformance?.[0]?.navDate || 'N/A'}</Text>
          </div>
        </div>

        {/* Level 1: Sub-sections */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

          {/* Main Column */}
          <div className="lg:col-span-2 flex flex-col gap-6">
            
            {/* Level 2 Card: Glassmorphism returns AreaChart */}
            <div className="bg-white/60 dark:bg-white/5 backdrop-blur-[20px] rounded-2xl p-8 border border-slate-200 dark:border-white/5 overflow-hidden relative shadow-xl dark:shadow-none transition-colors duration-300">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-8 gap-4">
                <Title className="text-2xl font-medium font-display text-slate-900 dark:text-white">Performance</Title>
                <div className="flex bg-slate-200/60 dark:bg-black/40 backdrop-blur-md rounded-xl p-1 overflow-x-auto custom-scrollbar border border-slate-300/50 dark:border-white/5 hide-scrollbar">
                  {['1D', '1W', '1M', '3M', '6M', 'YTD', '1Y', '3Y', '5Y'].map((period) => (
                    <button
                      key={period}
                      onClick={() => setSelectedPeriod(period)}
                      className={`px-4 py-1.5 text-sm font-medium rounded-lg transition-all whitespace-nowrap ${
                        selectedPeriod === period 
                        ? 'bg-primary/10 dark:bg-primary/20 text-primary shadow-sm border border-primary/20' 
                        : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-black/5 dark:hover:bg-white/5 border border-transparent'
                      }`}
                    >
                      {period}
                    </button>
                  ))}
                </div>
              </div>

              <div className="h-72 w-full mt-4 mb-8">
                <AreaChart
                  className="h-72 text-slate-900 dark:text-white"
                  data={chartData}
                  index="date"
                  categories={["Return"]}
                  colors={["blue"]}
                  valueFormatter={(val) => `${val}%`}
                  yAxisWidth={45}
                  showAnimation={true}
                  showLegend={false}
                  showGridLines={false}
                />
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6 px-4 text-center">
                {[
                  { label: 'YTD', val: profile.fundPerformance?.[0]?.pYtdReturn },
                  { label: '3M', val: profile.fundPerformance?.[0]?.p3mReturn },
                  { label: '1Y', val: profile.fundPerformance?.[0]?.p1yReturn },
                  { label: '3Y', val: profile.fundPerformance?.[0]?.p3yReturn },
                ].map(({ label, val }) => {
                  const numericVal = val ? Number(val) : NaN;
                  let colorClass = 'text-slate-500 dark:text-slate-400';
                  if (!isNaN(numericVal)) {
                    if (numericVal > 0) colorClass = 'text-emerald-600 dark:text-emerald-400';
                    else if (numericVal < 0) colorClass = 'text-rose-400 dark:text-rose-400';
                  }
                  
                  return (
                    <div key={label}>
                      <Text className="text-slate-500 dark:text-slate-400 text-sm mb-1 uppercase tracking-wider">{label}</Text>
                      <Metric className={`text-2xl font-display ${colorClass}`}>
                        {!isNaN(numericVal) ? `${numericVal > 0 ? '+' : ''}${numericVal.toFixed(2)}%` : '-'}
                      </Metric>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="bg-white/60 dark:bg-white/5 backdrop-blur-[20px] rounded-2xl p-8 border border-slate-200 dark:border-white/5 shadow-xl dark:shadow-none transition-colors duration-300">
              <Title className="text-2xl font-medium mb-6 font-display text-slate-900 dark:text-white">Asset Allocation</Title>
              {allocationData.length > 0 ? (
                
                console.log("allocationData",allocationData),

                <div className="flex flex-col md:flex-row items-center gap-8">
                  <div className="w-full md:w-1/2 flex justify-center">
                    <DonutChart
                      className="h-56"
                      data={allocationData}
                      category="value"
                      index="name"
                      valueFormatter={(val) => `${Number(val).toFixed(2)}%`}
                      colors={["emerald", "blue", "violet", "amber", "rose", "cyan", "fuchsia"]}
                      showAnimation={true}
                      showLabel={false}
                    />
                    
                   
                  </div>
                  <div className="w-full md:w-1/2">
                    <List className="mt-2 text-slate-700 dark:text-slate-300">
                      {allocationData.map((item: any) => (
                        <ListItem key={item.name}>
                          <span>{item.name}</span>
                          <span className="font-medium">{item.value.toFixed(2)}%</span>
                        </ListItem>
                      ))}
                    </List>
                  </div>
                </div>
              ) : (
                <Text className="text-slate-500 dark:text-slate-400">No asset allocation data available for this fund.</Text>
              )}
            </div>

            <div className="bg-white/60 dark:bg-white/5 backdrop-blur-[20px] rounded-2xl p-8 border border-slate-200 dark:border-white/5 shadow-xl dark:shadow-none transition-colors duration-300">
              <Title className="text-2xl font-medium mb-6 font-display text-slate-900 dark:text-white">Top Holdings</Title>
              {topHoldingData.length > 0 ? (
                <div className="flex flex-col md:flex-row items-center gap-8">
                  <div className="w-full md:w-1/2 flex justify-center">
                    <DonutChart
                      className="h-56"
                      data={topHoldingData}
                      category="value"
                      index="name"
                      valueFormatter={(val) => `${Number(val).toFixed(2)}%`}
                      colors={["emerald", "blue", "violet", "amber", "rose", "cyan", "fuchsia"]}
                      showAnimation={true}
                      showLabel={false}
                    />
                  </div>
                  <div className="w-full md:w-1/2">
                    <List className="mt-2 text-slate-700 dark:text-slate-300">
                      {topHoldingData.map((item: { name: string, value: number }) => (
                        <ListItem key={item.name}>
                          <span className="truncate max-w-[200px]" title={item.name}>{item.name}</span>
                          <span className="font-medium">{item.value.toFixed(2)}%</span>
                        </ListItem>
                      ))}
                    </List>
                  </div>
                </div>
              ) : (
                <Text className="text-slate-500 dark:text-slate-400">No top holdings data available for this fund.</Text>
              )}
            </div>

            <div className="bg-white/60 dark:bg-white/5 backdrop-blur-[20px] rounded-2xl p-8 border border-slate-200 dark:border-white/5 shadow-xl dark:shadow-none transition-colors duration-300">
              <Title className="text-2xl font-medium mb-6 font-display text-slate-900 dark:text-white">AI Analyst Insight</Title>
              {profile.aiInsight && profile.aiInsight.length > 0 ? (
                <Text className="text-slate-700 dark:text-slate-300 text-lg leading-relaxed font-inter">
                  {profile.aiInsight[0].content}
                </Text>
              ) : (
                <Text className="text-slate-500 dark:text-slate-400">No AI insights available for this fund.</Text>
              )}
            </div>
            
          </div>

          {/* Right Column */}
          <div className="flex flex-col gap-6">
            
            <div className="bg-white/60 dark:bg-white/5 backdrop-blur-[20px] rounded-2xl p-8 border border-slate-200 dark:border-white/5 shadow-xl dark:shadow-none transition-colors duration-300">
              <Title className="text-xl font-medium mb-6 font-display text-slate-900 dark:text-white">Key Statistics</Title>
              <div className="flex flex-col gap-6">
                <div>
                  <Text className="text-slate-500 dark:text-slate-400 text-sm">Standard Deviation</Text>
                  <Text className="text-xl text-slate-900 dark:text-white font-display mt-1">{profile.fundAnalysis?.[0]?.standardDeviation || 'N/A'}</Text>
                </div>
                <div>
                  <Text className="text-slate-500 dark:text-slate-400 text-sm">Treynor Ratio</Text>
                  <Text className="text-xl text-slate-900 dark:text-white font-display mt-1">{profile.fundAnalysis?.[0]?.treynorRatio || 'N/A'}</Text>
                </div>
                <div>
                  <Text className="text-slate-500 dark:text-slate-400 text-sm">Sortino Ratio</Text>
                  <Text className="text-xl text-slate-900 dark:text-white font-display mt-1">{profile.fundAnalysis?.[0]?.sortinoRatio || 'N/A'}</Text>
                </div>
                <div>
                  <Text className="text-slate-500 dark:text-slate-400 text-sm">Information Ratio</Text>
                  <Text className="text-xl text-slate-900 dark:text-white font-display mt-1">{profile.fundAnalysis?.[0]?.informationRatio || 'N/A'}</Text>
                </div>
              </div>
            </div>

            <div className="bg-white/60 dark:bg-white/5 backdrop-blur-[20px] rounded-2xl p-8 border border-slate-200 dark:border-white/5 shadow-xl dark:shadow-none transition-colors duration-300">
              <Title className="text-xl font-medium mb-6 font-display text-slate-900 dark:text-white">Fund Details</Title>
              <div className="flex flex-col gap-6">
                <div>
                  <Text className="text-slate-500 dark:text-slate-400 text-sm">Regist. Date</Text>
                  <Text className="text-lg text-slate-900 dark:text-white font-display mt-1">{profile.registrationDate || '-'}</Text>
                </div>
                <div>
                  <Text className="text-slate-500 dark:text-slate-400 text-sm">Min Initial Purchase</Text>
                  <Text className="text-lg text-primary font-display mt-1">{profile.fstLowbuyVal ? Number(profile.fstLowbuyVal).toLocaleString() + ' THB' : '-'}</Text>
                </div>
                <Divider className="my-1" />
                <div>
                  <Text className="text-slate-500 dark:text-slate-400 text-sm">Tax Type</Text>
                  <Text className="text-lg text-slate-900 dark:text-white font-display mt-1">{profile.taxType || '-'}</Text>
                </div>
                <div>
                  <Text className="text-slate-500 dark:text-slate-400 text-sm">Dividend Policy</Text>
                  <Text className="text-lg text-slate-900 dark:text-white font-display mt-1">{profile.dividendFlag === 'Y' ? 'Dividend yield' : 'No dividend'}</Text>
                </div>
                <div>
                  <Text className="text-slate-500 dark:text-slate-400 text-sm">Fund Policy</Text>
                  <Text className="text-lg text-slate-900 dark:text-white font-display mt-1">{profile.fundPolicy}</Text>
                </div>
              </div>
            </div>

            <div className="bg-white/60 dark:bg-white/5 backdrop-blur-[20px] rounded-2xl p-8 border border-slate-200 dark:border-white/5 shadow-xl dark:shadow-none transition-colors duration-300">
               <Title className="text-xl font-medium mb-4 font-display text-slate-900 dark:text-white">Documentation</Title>
               <button className="w-full text-left bg-slate-200/60 dark:bg-black/40 hover:bg-slate-300/80 dark:hover:bg-white/10 transition-colors rounded-xl p-4 flex items-center justify-between group border border-slate-300/50 dark:border-white/5">
                  <Text className="font-medium text-slate-900 dark:text-white group-hover:text-primary transition-colors">Fund Fact Sheet</Text>
                  <span className="text-slate-500 group-hover:text-primary transition-colors text-xl">↓</span>
               </button>
            </div>

          </div>

        </div>
      </section>
    </main>
  );
}
