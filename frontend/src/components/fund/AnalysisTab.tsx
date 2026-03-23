import React from 'react';
import { FundDetail, FundAnalysis, AiInsight } from '@/lib/api/fundDecision';
import { Sparkles, BarChart3, TrendingUp, BookOpen } from 'lucide-react';

function fmt(value: number | null | undefined, decimals = 2, suffix = '') {
  if (value === null || value === undefined) return '—';
  return `${value.toLocaleString(undefined, { minimumFractionDigits: decimals, maximumFractionDigits: decimals })}${suffix}`;
}

const SENTIMENT_CONFIG = {
  LOW:  { label: 'Low Impact',  bar: 'bg-yellow-400',  text: 'text-yellow-300',  bgBadge: 'bg-yellow-400/15 border-yellow-400/30' },
  MED:  { label: 'Med Impact',  bar: 'bg-orange-400',  text: 'text-orange-300',  bgBadge: 'bg-orange-400/15 border-orange-400/30' },
  HIGH: { label: 'High Impact', bar: 'bg-rose-500',    text: 'text-rose-300',    bgBadge: 'bg-rose-500/15   border-rose-500/30' },
};

function SentimentGauge({ score }: { score: number | null }) {
  if (score === null) return <span className="text-slate-500 text-sm">—</span>;
  const pct = ((score + 1) / 2) * 100; // map -1..1 → 0..100
  const label = score > 0.35 ? 'Bullish 🐂' : score < -0.35 ? 'Bearish 🐻' : 'Neutral ⚖️';
  const textColor = score > 0.35 ? 'text-emerald-300' : score < -0.35 ? 'text-rose-300' : 'text-yellow-300';
  const markerColor = score > 0.35 ? 'bg-emerald-400' : score < -0.35 ? 'bg-rose-500' : 'bg-yellow-400';
  
  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <span className="text-xs font-bold text-slate-500 uppercase tracking-widest">Sentiment</span>
        <span className={`font-bold text-sm ${textColor} px-3 py-1 rounded-full bg-white/5 border border-white/10`}>
          {label}
        </span>
      </div>
      <div className="relative h-3 rounded-full overflow-hidden bg-slate-900 border border-white/5" style={{ background: 'linear-gradient(90deg, #f43f5e 0%, #3b82f6 50%, #10b981 100%)' }}>
        <div
          className={`absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-5 h-5 rounded-full border-4 border-slate-950 shadow-2xl transition-all duration-1000 ${markerColor}`}
          style={{ left: `${pct}%` }}
        />
      </div>
      <div className="flex justify-between text-[10px] text-slate-500 font-bold uppercase tracking-wider">
        <span>Extremely Bearish</span>
        <span>Neutral</span>
        <span>Extremely Bullish</span>
      </div>
    </div>
  );
}

function AnalysisStat({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <div className="p-4 bg-white/5 rounded-xl border border-white/10 space-y-1 group hover:bg-white/10 transition-colors">
      <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider group-hover:text-slate-400">{label}</p>
      <p className="text-2xl font-bold text-foreground tabular-nums group-hover:text-primary transition-colors">{value}</p>
      {hint && <p className="text-[10px] text-slate-500 font-medium">{hint}</p>}
    </div>
  );
}

interface AnalysisTabProps {
  fund: FundDetail;
}

export const AnalysisTab: React.FC<AnalysisTabProps> = ({ fund }) => {
  const analysis = fund.fund_analysis?.[0] || null;

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Left Col: AI Insights */}
        <div className="space-y-6">
          <div className="flex items-center gap-2 text-foreground">
            <Sparkles className="w-5 h-5 text-primary" />
            <h2 className="text-xl font-bold">AI Insights & Perspective</h2>
          </div>

          <div className="space-y-4">
            {fund.latest_insight && (
              <div className="p-6 rounded-2xl bg-primary/10 border border-primary/20 relative group hover:bg-primary/15 transition-all">
                <div className="absolute -top-3 left-6 px-3 py-1 rounded-full bg-primary text-white text-[10px] font-bold uppercase tracking-[0.2em] shadow-lg shadow-primary/40">
                  Daily Spark
                </div>
                <p className="text-slate-200 text-base leading-relaxed italic mb-4 mt-2">
                  &quot;{fund.latest_insight.content}&quot;
                </p>
                <div className="flex items-center justify-between text-[10px] font-bold uppercase tracking-widest text-slate-500">
                  <span className="flex items-center gap-1.5"><TrendingUp className="w-3 h-3" /> Potential Optimized</span>
                  <span>{new Date(fund.latest_insight.created_at || '').toLocaleDateString()}</span>
                </div>
              </div>
            )}

            {fund.ai_insights.length === 0 && !fund.latest_insight ? (
              <div className="flex flex-col items-center justify-center py-20 glass rounded-2xl border border-white/10 gap-3 text-slate-500">
                <Sparkles className="w-10 h-10 opacity-20" />
                <p className="text-sm font-medium">Seeking insights...</p>
              </div>
            ) : (
              <div className="space-y-3">
                {fund.ai_insights.map((insight, i) => (
                  <div key={i} className="flex gap-4 p-5 glass rounded-2xl border border-white/5 hover:border-white/20 transition-all hover:translate-x-1">
                    <div className="mt-1.5 shrink-0">
                      <div className="w-2.5 h-2.5 rounded-full bg-primary shadow-[0_0_12px_rgba(59,130,246,0.8)]" />
                    </div>
                    <div className="space-y-2">
                      <p className="text-sm text-slate-300 leading-relaxed font-medium">
                        {insight.content}
                      </p>
                      {insight.created_at && (
                        <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">
                          {new Date(insight.created_at).toLocaleDateString()}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Col: Advanced Analysis */}
        <div className="space-y-6">
          <div className="flex items-center gap-2 text-foreground">
            <BarChart3 className="w-5 h-5 text-primary" />
            <h2 className="text-xl font-bold">Advanced Quantitative Analysis</h2>
          </div>

          {!analysis ? (
             <div className="flex flex-col items-center justify-center py-32 glass rounded-2xl border border-white/10 gap-4 text-slate-500">
                <BookOpen className="w-12 h-12 opacity-20" />
                <p className="text-sm font-medium text-center">No quantitative analysis<br/>calculated for this fund yet.</p>
             </div>
          ) : (
            <div className="space-y-6">
              <div className="glass rounded-2xl border border-white/10 p-6 space-y-6">
                <SentimentGauge score={analysis.sentiment_score} />
                {analysis.sentiment_summary && (
                  <div className="p-4 rounded-xl bg-white/5 border-l-4 border-primary italic">
                    <p className="text-sm text-slate-300 leading-relaxed">
                      &quot;{analysis.sentiment_summary}&quot;
                    </p>
                  </div>
                )}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <AnalysisStat label="Std Deviation"     value={fmt(analysis.standard_deviation, 4)}   hint="Volatility measure" />
                <AnalysisStat label="Treynor Ratio"     value={fmt(analysis.treynor_ratio, 4)}         hint="Return per unit of Beta" />
                <AnalysisStat label="Sortino Ratio"     value={fmt(analysis.sortino_ratio, 4)}         hint="Return vs Downside Risk" />
                <AnalysisStat label="Information Ratio" value={fmt(analysis.information_ratio, 4)}     hint="Manager skill alpha" />
                <AnalysisStat label="Upside Capture"    value={fmt(analysis.capture_ratio_up, 2, '%')} hint="Performance in up markets" />
                <AnalysisStat label="Downside Capture"  value={fmt(analysis.capture_ratio_down, 2, '%')} hint="Protection in down markets" />
              </div>

              <div className="flex justify-between items-center text-[10px] font-bold text-slate-600 uppercase tracking-widest px-2">
                <span>Calc Version: 2.1.0-STABLE</span>
                <span>Last Updated: {new Date(analysis.updated_at || '').toLocaleDateString()}</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
