import React from 'react';
import { FundDetail } from '@/lib/api/fundDecision';
import { Layers, PieChart } from 'lucide-react';

interface HoldingsTabProps {
  fund: FundDetail;
}

export const HoldingsTab: React.FC<HoldingsTabProps> = ({ fund }) => {
  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-foreground">
          <Layers className="w-5 h-5 text-primary" />
          <h2 className="text-xl font-bold">Top Holdings</h2>
        </div>
        <div className="flex items-center gap-4 text-xs font-semibold text-slate-500 uppercase tracking-widest">
           <span className="flex items-center gap-1.5"><div className="w-2 h-2 rounded-full bg-primary" /> {fund.holdings.length} Assets</span>
        </div>
      </div>

      {fund.holdings.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-24 glass rounded-2xl border border-white/10 gap-4 text-slate-500">
          <div className="w-16 h-16 rounded-full bg-white/5 flex items-center justify-center">
            <PieChart className="w-8 h-8 opacity-20" />
          </div>
          <div className="text-center">
            <p className="text-lg font-semibold text-slate-400">No Holdings Data</p>
            <p className="text-sm">Detailed holding information is currently unavailable for this fund.</p>
          </div>
        </div>
      ) : (
        <div className="glass rounded-2xl border border-white/10 overflow-hidden shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-white/5 border-b border-white/10 text-left text-[10px] text-slate-500 font-bold uppercase tracking-[0.2em]">
                  <th className="px-8 py-5">Asset Name</th>
                  <th className="px-8 py-5 text-right w-40">Weight (%)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {fund.holdings.map((holding, i) => (
                  <tr key={i} className="group hover:bg-white/5 transition-all duration-300">
                    <td className="px-8 py-5">
                      <div className="flex items-center gap-4">
                        <span className="flex items-center justify-center w-8 h-8 rounded-lg bg-white/5 text-[10px] font-bold text-slate-500 group-hover:bg-primary/20 group-hover:text-primary transition-colors">
                          {i + 1}
                        </span>
                        <span className="font-semibold text-slate-200 group-hover:text-foreground transition-colors truncate max-w-md">
                          {holding.name || `Asset ${i + 1}`}
                        </span>
                      </div>
                    </td>
                    <td className="px-8 py-5 text-right">
                      <div className="flex items-center justify-end gap-3">
                         <div className="w-24 h-1.5 rounded-full bg-white/5 overflow-hidden hidden sm:block">
                            <div 
                              className="h-full bg-primary transition-all duration-1000 group-hover:scale-x-105 origin-left" 
                              style={{ width: `${holding.weight || 0}%` }}
                            />
                         </div>
                         <span className="font-mono font-bold text-primary tabular-nums">
                           {holding.weight !== undefined ? Number(holding.weight).toFixed(2) : '—'}%
                         </span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="bg-white/5 px-8 py-4 border-t border-white/10">
            <p className="text-xs text-slate-500 italic">
              * Data represents top holdings as of the last available reporting period.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
