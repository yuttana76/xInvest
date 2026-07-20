import React from 'react';
import { FundDetail } from '@/lib/api/fundDecision';
import { ShieldAlert, CheckCircle, XCircle, ExternalLink, FileText } from 'lucide-react';

const RISK_LABELS: Record<number, { label: string; color: string }> = {
  1: { label: 'Very Low Risk',        color: 'text-emerald-400' },
  2: { label: 'Low Risk',             color: 'text-green-400' },
  3: { label: 'Medium-Low Risk',      color: 'text-yellow-400' },
  4: { label: 'Medium-High Risk',     color: 'text-orange-400' },
  5: { label: 'High Risk',            color: 'text-red-400' },
  6: { label: 'Very High Risk',       color: 'text-rose-500' },
  7: { label: 'Very High Risk (Sp.)', color: 'text-rose-600' },
  8: { label: 'Maximum Risk',         color: 'text-red-600' },
};

interface FundHeaderProps {
  fund: FundDetail;
}

export const FundHeader: React.FC<FundHeaderProps> = ({ fund }) => {
  const riskInfo = RISK_LABELS[fund.risk_level] ?? { label: `Level ${fund.risk_level}`, color: 'text-slate-400' };

  return (
    <div className="glass rounded-2xl border border-white/10 shadow-2xl p-6 mb-6">
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-6">
        <div className="space-y-3">
          <div className="flex flex-wrap items-center gap-2">
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-blue-500/10 text-blue-300 border border-blue-500/20">
              {fund.fund_category}
            </span>
            {fund.is_dividend ? (
              <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
                <CheckCircle className="w-3 h-3" /> Dividend
              </span>
            ) : (
              <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-white/5 text-slate-400 border border-white/10">
                <XCircle className="w-3 h-3" /> Accumulation
              </span>
            )}
            <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-white/10 border border-white/10 ${riskInfo.color}`}>
              <ShieldAlert className="w-3 h-3" />
              {riskInfo.label}
            </span>
          </div>

          <div>
            <h1 className="text-4xl font-bold text-white tracking-tight leading-none group">
              {fund.fundCode}
              <span className="ml-2 opacity-0 group-hover:opacity-100 transition-opacity text-sm font-normal text-slate-500">#{fund.id}</span>
            </h1>
            <p className="text-slate-300 text-lg mt-1">{fund.name_th}</p>
            {fund.name_en !== fund.name_th && (
              <p className="text-slate-500 text-sm mt-0.5 italic">{fund.name_en}</p>
            )}
          </div>
        </div>

        <div className="flex flex-col gap-2 shrink-0">
          {fund.fact_sheet_url && (
            <a
              href={fund.fact_sheet_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-300 hover:bg-blue-500/20 transition-all text-sm font-medium hover:scale-[1.02] active:scale-[0.98]"
            >
              <ExternalLink className="w-4 h-4" /> Fact Sheet (Web)
            </a>
          )}
          {fund.fact_sheet_pdf && (
            <a
              href={fund.fact_sheet_pdf}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 hover:bg-rose-500/20 transition-all text-sm font-medium hover:scale-[1.02] active:scale-[0.98]"
            >
              <FileText className="w-4 h-4" /> Fact Sheet (PDF)
            </a>
          )}
          {!fund.fact_sheet_url && !fund.fact_sheet_pdf && (
            <span className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-slate-500 text-sm italic">
              <FileText className="w-4 h-4" /> No Fact Sheet Available
            </span>
          )}
        </div>
      </div>
    </div>
  );
};
