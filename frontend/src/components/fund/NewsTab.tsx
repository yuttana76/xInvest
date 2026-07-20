import React from 'react';
import { FundDetail } from '@/lib/api/fundDecision';
import { Newspaper, ExternalLink, Calendar, TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface NewsTabProps {
  fund: FundDetail;
}

export const NewsTab: React.FC<NewsTabProps> = ({ fund }) => {
  const news = fund.approved_news || [];

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex items-center gap-2 text-foreground mb-4">
        <Newspaper className="w-5 h-5 text-primary" />
        <h2 className="text-xl font-bold">Related News & Catalysts</h2>
      </div>

      {news.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-24 glass rounded-2xl border border-white/10 gap-4 text-slate-500">
          <div className="w-16 h-16 rounded-full bg-white/5 flex items-center justify-center">
            <Newspaper className="w-8 h-8 opacity-20" />
          </div>
          <p className="text-lg font-semibold text-slate-400">No related news found.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {news.map((item) => (
            <div key={item.id} className="glass rounded-2xl border border-white/10 overflow-hidden flex flex-col group hover:border-primary/50 transition-all duration-300 hover:shadow-2xl hover:shadow-primary/10">
              <div className="p-6 flex-1 space-y-4">
                <div className="flex items-center justify-between">
                  <span className="px-3 py-1 rounded-full bg-primary/10 text-primary text-[10px] font-bold uppercase tracking-widest border border-primary/20">
                    {item.source}
                  </span>
                  <div className="flex items-center gap-1.5 text-slate-500 text-[10px] font-bold uppercase tracking-widest">
                    <Calendar className="w-3 h-3" />
                    {new Date(item.published_at).toLocaleDateString()}
                  </div>
                </div>

                <h3 className="text-lg font-bold text-foreground leading-tight group-hover:text-primary transition-colors line-clamp-2">
                  {item.title}
                </h3>

                <p className="text-sm text-slate-400 leading-relaxed line-clamp-3">
                  {item.content}
                </p>

                {item.ai_summary && (
                  <div className="p-4 rounded-xl bg-white/5 border border-white/5 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">AI IMPACT ANALYSIS</span>
                      {item.ai_sentiment_score !== null && (
                         <div className="flex items-center gap-1">
                            {item.ai_sentiment_score > 0.1 ? <TrendingUp className="w-3 h-3 text-emerald-400" /> : item.ai_sentiment_score < -0.1 ? <TrendingDown className="w-3 h-3 text-rose-400" /> : <Minus className="w-3 h-3 text-yellow-400" />}
                            <span className={`text-[10px] font-bold ${item.ai_sentiment_score > 0.1 ? 'text-emerald-400' : item.ai_sentiment_score < -0.1 ? 'text-rose-400' : 'text-yellow-400'}`}>
                               {(item.ai_sentiment_score * 100).toFixed(0)}%
                            </span>
                         </div>
                      )}
                    </div>
                    <p className="text-xs text-slate-300 font-medium italic">
                      &quot;{item.ai_summary}&quot;
                    </p>
                  </div>
                )}
              </div>

              <a 
                href={item.url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="bg-white/5 border-t border-white/10 px-6 py-4 flex items-center justify-between text-xs font-bold text-slate-400 hover:bg-white/10 hover:text-white transition-all group/link"
              >
                <span>READ FULL ARTICLE</span>
                <ExternalLink className="w-4 h-4 group-hover/link:translate-x-1 group-hover/link:-translate-y-1 transition-transform" />
              </a>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
