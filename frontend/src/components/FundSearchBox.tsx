'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Search } from 'lucide-react';
import { Button } from './Button';

interface FundSearchBoxProps {
    className?: string;
    placeholder?: string;
}

export const FundSearchBox: React.FC<FundSearchBoxProps> = ({ 
    className = "", 
    placeholder = "Search by fund name, policy or keyword (e.g. กองทุนลดหย่อนภาษี)..." 
}) => {
    const router = useRouter();
    const [searchQuery, setSearchQuery] = useState('');

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        if (searchQuery.trim()) {
            router.push(`/fund/${encodeURIComponent(searchQuery)}`);
        }
    };

    return (
        <form onSubmit={handleSearch} className={`flex flex-col sm:flex-row gap-4 items-center ${className}`}>
            <div className="relative flex-1 w-full group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <Search className="h-5 w-5 text-slate-400 group-focus-within:text-primary transition-colors" />
                </div>
                <input
                    type="text"
                    placeholder={placeholder}
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full bg-white/3 text-white placeholder:text-slate-500 rounded-2xl pl-12 pr-4 py-4 border border-white/10 focus:border-primary/50 focus:bg-white/5 focus:outline-none focus:ring-4 focus:ring-primary/10 transition-all shadow-inner"
                />
                <div className="absolute inset-x-0 bottom-0 h-px bg-linear-to-r from-transparent via-primary/50 to-transparent opacity-0 group-focus-within:opacity-100 transition-opacity" />
            </div>
            <Button type="submit" size="lg" 
                className="rounded-2xl px-8 h-[58px] w-full sm:w-auto font-medium shadow-lg shadow-primary/25 hover:shadow-primary/40 transition-all">
                Explore Insights
            </Button>
        </form>
    );
};
