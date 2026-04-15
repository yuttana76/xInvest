'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useApolloClient } from '@apollo/client';
import { GET_FUND_PROFILE_BY_CODE } from '@/lib/graphql/queries';
import { Search } from 'lucide-react';
import { Button } from './Button';

interface FundSearchBoxProps {
    className?: string;
    placeholder?: string;
}

export const FundSearchBox: React.FC<FundSearchBoxProps> = ({ 
    className = "", 
    placeholder = "Search by fund code (e.g. BONE-EQ)..." 
}) => {
    const router = useRouter();
    const client = useApolloClient();
    const [searchQuery, setSearchQuery] = useState('');
    const [isSearching, setIsSearching] = useState(false);
    const [errorMsg, setErrorMsg] = useState('');

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        const code = searchQuery.trim().toUpperCase();
        if (!code) return;

        setIsSearching(true);
        setErrorMsg('');

        try {
            const { data } = await client.query({
                query: GET_FUND_PROFILE_BY_CODE,
                variables: { fundCode: code }
            });

            if (data?.fundProfileByCode) {
                router.push(`/discovery/${encodeURIComponent(code)}`);
            } else {
                setErrorMsg('Fund not found. Please try another code.');
            }
        } catch (error) {
            console.error("GraphQL Search Error:", error);
            setErrorMsg('Error searching for fund. Please try again.');
        } finally {
            setIsSearching(false);
        }
    };

    return (
        <div className="flex flex-col gap-2 w-full">
            <form onSubmit={handleSearch} className={`flex flex-col sm:flex-row gap-4 items-center ${className}`}>
                <div className="relative flex-1 w-full group">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <Search className={`h-5 w-5 transition-colors ${errorMsg ? 'text-red-500 dark:text-red-400' : 'text-slate-500 dark:text-slate-400 group-focus-within:text-primary'}`} />
                    </div>
                    <input
                        type="text"
                        placeholder={placeholder}
                        value={searchQuery}
                        onChange={(e) => { setSearchQuery(e.target.value); setErrorMsg(''); }}
                        disabled={isSearching}
                        className={`w-full bg-white/60 dark:bg-white/3 text-slate-900 dark:text-white placeholder:text-slate-400 dark:placeholder:text-slate-500 rounded-2xl pl-12 pr-4 py-4 border ${errorMsg ? 'border-red-500/50 focus:border-red-500/50 focus:ring-red-500/10' : 'border-slate-300 dark:border-white/10 focus:border-primary/50 focus:ring-primary/10'} focus:bg-white dark:focus:bg-white/5 focus:outline-none focus:ring-4 transition-all shadow-inner`}
                    />
                    <div className={`absolute inset-x-0 bottom-0 h-px bg-linear-to-r opacity-0 group-focus-within:opacity-100 transition-opacity ${errorMsg ? 'from-transparent via-red-500/50 to-transparent' : 'from-transparent via-primary/50 to-transparent'}`} />
                </div>
                <Button type="submit" size="lg" disabled={isSearching}
                    className={`rounded-2xl px-8 h-[58px] w-full sm:w-auto font-medium shadow-lg transition-all ${isSearching ? 'opacity-70 cursor-not-allowed' : 'shadow-primary/25 hover:shadow-primary/40'}`}>
                    {isSearching ? 'Searching...' : 'Explore Insights'}
                </Button>
            </form>
            {errorMsg && (
                <p className="text-red-600 dark:text-red-400 text-sm font-medium px-4">{errorMsg}</p>
            )}
        </div>
    );
};
