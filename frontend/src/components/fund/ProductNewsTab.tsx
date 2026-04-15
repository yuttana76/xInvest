import React, { useEffect, useState } from 'react';
import { Newspaper, ExternalLink } from 'lucide-react';
import { NewsArticle } from '@/lib/api/fundDecision';
import { getNewsByProduct } from '@/lib/api/news';

interface ProductNewsTabProps {
  productType?: 'mf' | 'pf' | 'bond';
  ticker?: string;
  initialNews?: NewsArticle[];
}

export const ProductNewsTab: React.FC<ProductNewsTabProps> = ({ productType, ticker, initialNews }) => {
  const [news, setNews] = useState<NewsArticle[]>(initialNews || []);
  const [loading, setLoading] = useState(!initialNews);

  useEffect(() => {
    if (initialNews) return;

    const fetchNews = async () => {
      setLoading(true);
      try {
        const data = await getNewsByProduct(productType, ticker);
        setNews(data);
      } catch (error) {
        console.error('Failed to fetch news:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchNews();
  }, [productType, ticker, initialNews]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-24 gap-4">
        <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
        <p className="text-slate-500 dark:text-slate-400 text-sm animate-pulse">Fetching latest news...</p>
      </div>
    );
  }

  return (
    <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex items-center gap-2 text-slate-800 dark:text-foreground mb-6">
        <Newspaper className="w-5 h-5 text-primary" />
        <h2 className="text-xl font-bold tracking-tight">Market Intelligence & Catalysts</h2>
      </div>

      {news.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-24 glass rounded-3xl border border-slate-200 dark:border-white/10 gap-4 text-slate-500">
          <div className="w-20 h-20 rounded-full bg-slate-100 dark:bg-white/5 flex items-center justify-center">
            <Newspaper className="w-10 h-10 opacity-20" />
          </div>
          <p className="text-lg font-semibold text-slate-600 dark:text-slate-400">No related news for this asset.</p>
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {news.map((item) => (
            <div key={item.id} className="group relative glass rounded-2xl border border-slate-200 dark:border-white/5 hover:border-primary/30 transition-all duration-500 hover:shadow-xl dark:hover:shadow-2xl dark:hover:shadow-primary/5 overflow-hidden">
              <div className="p-5 flex flex-col md:flex-row md:items-center gap-6">
                {/* Date & Source Column */}
                <div className="flex md:flex-col items-center md:items-start gap-2 md:gap-1 min-w-[100px]">
                  <span className="text-[10px] font-black text-primary uppercase tracking-tighter">
                    {new Date(item.published_at).toLocaleDateString('en-GB', { day: '2-digit', month: 'short' })}
                  </span>
                  <div className="px-2 py-0.5 rounded-md bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 text-[9px] font-bold text-slate-500 uppercase">
                    {item.source}
                  </div>
                </div>

                {/* Content Column */}
                <div className="flex-1 space-y-2">
                  <a 
                    href={item.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="block hover:text-primary transition-colors text-slate-800 dark:text-slate-100"
                  >
                    <h3 className="text-base font-bold leading-tight line-clamp-2">
                      {item.title}
                    </h3>
                  </a>
                  <p className="text-xs text-slate-600 dark:text-slate-400 line-clamp-1 opacity-70 group-hover:opacity-100 transition-opacity">
                    {item.content}
                  </p>
                </div>

                {/* Analysis Indicators (Only if approved) */}
                <div className="flex items-center gap-3">
                  {item.fund_supervisor_approve ? (
                    <>
                      {/* FM Sentiment Mini (Strategy) */}
                      <div className="flex flex-col items-end">
                        <span className="text-[8px] font-black text-slate-500 uppercase tracking-widest mb-1">STRATEGY</span>
                        <div className={`flex items-center gap-1 px-2 py-1 rounded-lg border ${
                          item.fm_sentiment_score && item.fm_sentiment_score > 0.1 
                            ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-600 dark:text-primary' 
                            : item.fm_sentiment_score && item.fm_sentiment_score < -0.1 
                              ? 'bg-rose-500/10 border-rose-500/20 text-rose-600 dark:text-rose-500' 
                              : 'bg-slate-100 dark:bg-slate-500/10 border-slate-200 dark:border-slate-500/20 text-slate-500 dark:text-slate-400'
                        }`}>
                          <span className="text-[10px] font-bold">{item.fm_impact_level || 'N/A'}</span>
                        </div>
                      </div>
                    </>
                  ) : (
                    <div className="px-3 py-1.5 rounded-xl bg-slate-100 dark:bg-white/5 border border-dashed border-slate-300 dark:border-white/10 text-[9px] font-bold text-slate-400 dark:text-slate-600 uppercase tracking-widest">
                      Analysis Pending
                    </div>
                  )}
                  
                  <a 
                    href={item.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="w-10 h-10 rounded-xl bg-slate-200 dark:bg-white/5 flex items-center justify-center text-slate-600 dark:text-slate-500 hover:bg-primary hover:text-white transition-all duration-300"
                  >
                    <ExternalLink className="w-4 h-4" />
                  </a>
                </div>
              </div>

              {/* Expandable Analysis Section (if approved and has fm_summary) */}
              {item.fund_supervisor_approve && item.fm_summary && (
                <div className="px-5 pb-5 pt-0 animate-in slide-in-from-top-2 duration-300">
                  <div className="p-3 rounded-xl bg-amber-500/5 dark:bg-amber-500/5 border border-amber-500/10 dark:border-amber-500/10">
                    <p className="text-[14px] text-slate-600 dark:text-slate-400 font-medium leading-relaxed">
                      <span className="font-bold text-amber-600 dark:text-amber-500 mr-1">Analyst View:</span>
                      &quot;{item.fm_summary}&quot;
                    </p>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
