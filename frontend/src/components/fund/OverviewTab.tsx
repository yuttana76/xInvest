import React from 'react';
import { FundDetail } from '@/lib/api/fundDecision';
import { TrendingUp, TrendingDown, Minus, Info, Calendar, BarChart3 } from 'lucide-react';

function fmt(value: number | null | undefined, decimals = 2, suffix = '') {
  if (value === null || value === undefined) return '—';
  return `${value.toLocaleString(undefined, { minimumFractionDigits: decimals, maximumFractionDigits: decimals })}${suffix}`;
}

function fmtDate(iso: string | null | undefined) {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('en-GB', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

function MetricCard({
  label,
  value,
  icon,
  hint,
}: {
  label: string;
  value: string;
  icon?: React.ReactNode;
  hint?: string;
}) {
  return (
    <div className="flex flex-col gap-1 p-5 bg-white/5 hover:bg-white/10 transition-all rounded-2xl border border-white/10 group">
      <div className="flex items-center gap-1.5 text-xs text-slate-400 font-bold uppercase tracking-widest opacity-70 group-hover:opacity-100 transition-opacity">
        {icon && <span>{icon}</span>}
        {label}
      </div>
      <div className="text-3xl font-bold text-foreground mt-2 tracking-tight group-hover:text-primary transition-colors">{value}</div>
      {hint && <div className="text-xs text-slate-500 mt-1 font-medium">{hint}</div>}
    </div>
  );
}

interface OverviewTabProps {
  fund: FundDetail;
}

export const OverviewTab: React.FC<OverviewTabProps> = ({ fund }) => {
  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      {/* Performance Metrics */}
      <section>
        <div className="flex items-center gap-2 mb-6 text-foreground">
          <BarChart3 className="w-5 h-5 text-primary" />
          <h2 className="text-xl font-bold">Key Performance Metrics</h2>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <MetricCard
            label="Management Fee"
            value={fmt(fund.management_fee, 2, '%')}
            icon={<Info className="w-3.5 h-3.5" />}
            hint="Annual management cost"
          />
          <MetricCard
            label="Total Expense Ratio"
            value={fmt(fund.total_expense_ratio, 2, '%')}
            icon={<Info className="w-3.5 h-3.5" />}
            hint="All-in annual cost"
          />
          <MetricCard
            label="Sharpe Ratio"
            value={fmt(fund.sharpe_ratio, 4)}
            icon={<TrendingUp className="w-3.5 h-3.5" />}
            hint="Risk-adjusted return"
          />
          <MetricCard
            label="Alpha"
            value={fmt(fund.alpha, 4)}
            icon={
              fund.alpha !== null
                ? fund.alpha >= 0
                  ? <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />
                  : <TrendingDown className="w-3.5 h-3.5 text-rose-400" />
                : <Minus className="w-3.5 h-3.5" />
            }
            hint="Excess return vs Benchmark"
          />
          <MetricCard
            label="Beta"
            value={fmt(fund.beta, 4)}
            icon={<BarChart3 className="w-3.5 h-3.5" />}
            hint="Volatility vs Benchmark"
          />
          <MetricCard
            label="Max Drawdown"
            value={fmt(fund.max_drawdown, 2, '%')}
            icon={<TrendingDown className="w-3.5 h-3.5 text-rose-400" />}
            hint="Largest peak-to-trough decline"
          />
        </div>
      </section>

      {/* Fund Information */}
      <section>
        <div className="flex items-center gap-2 mb-6 text-foreground">
          <Calendar className="w-5 h-5 text-primary" />
          <h2 className="text-xl font-bold">Fund Information</h2>
        </div>
        <div className="glass rounded-2xl border border-white/10 p-8">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-x-8 gap-y-6">
            {[
              { label: 'Fund Code',      value: fund.fundCode },
              { label: 'AMC ID',         value: String(fund.amc) },
              { label: 'Risk Level',      value: `${fund.risk_level}` },
              { label: 'Fund Category',   value: fund.fund_category },
              { label: 'Last FFS Update', value: fmtDate(fund.last_updated_ffs) },
              { label: 'Created At',      value: fmtDate(fund.created_at) },
              { label: 'Last Updated',    value: fmtDate(fund.updated_at) },
              { label: 'Dividend Info',   value: fund.is_dividend ? 'Dividend Paying' : 'Accumulation' },
            ].map(({ label, value }) => (
              <div key={label} className="group">
                <p className="text-[10px] text-slate-500 font-bold uppercase tracking-[0.2em] mb-1 group-hover:text-slate-400 transition-colors">{label}</p>
                <p className="text-foreground font-semibold text-lg">{value}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};
