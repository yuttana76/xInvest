import React from 'react';
import { BarChart3, Layers, Sparkles, Newspaper } from 'lucide-react';

export type FundTabType = 'overview' | 'holdings' | 'analysis' | 'news';

interface FundTabsProps {
  activeTab: FundTabType;
  setActiveTab: (tab: FundTabType) => void;
  newsCount?: number;
}

export const FundTabs: React.FC<FundTabsProps> = ({ activeTab, setActiveTab, newsCount = 0 }) => {
  const tabs = [
    { id: 'overview' as const, label: 'Performance & Info', icon: <BarChart3 className="w-4 h-4" /> },
    { id: 'holdings' as const, label: 'Holdings', icon: <Layers className="w-4 h-4" /> },
    { id: 'analysis' as const, label: 'Analysis & AI', icon: <Sparkles className="w-4 h-4" /> },
    { id: 'news' as const, label: 'News', icon: <Newspaper className="w-4 h-4" />, count: newsCount },
  ];

  return (
    <div className="flex flex-wrap gap-2 mb-8 bg-white/5 p-1 rounded-2xl border border-white/10 backdrop-blur-md">
      {tabs.map((tab) => {
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`
              flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium transition-all duration-300
              ${isActive 
                ? 'bg-primary text-white shadow-lg shadow-primary/25 scale-100' 
                : 'text-slate-400 hover:text-white hover:bg-white/5 scale-95'
              }
            `}
          >
            {tab.icon}
            {tab.label}
            {tab.count !== undefined && tab.count > 0 && (
              <span className={`
                ml-1 px-1.5 py-0.5 rounded-full text-[10px] font-bold
                ${isActive ? 'bg-white/20 text-white' : 'bg-white/10 text-slate-400'}
              `}>
                {tab.count}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
};
