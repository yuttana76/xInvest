'use client';

import React from 'react';
import { Title, Text } from '@tremor/react';
import { Navbar } from '@/components/Navbar';
import { FundSearchBox } from '@/components/FundSearchBox';

export default function DiscoveryPage() {

    // const trendingThemes = [
    //     { title: "กองทุนลดหย่อนภาษี", desc: "Top choices for tax savings (SSF/RMF)" },
    //     { title: "หุ้นอเมริกา", desc: "Tech and growth opportunities in the US" },
    //     { title: "ตราสารหนี้", desc: "Safe haven for volatile markets" },
    //     { title: "หุ้นปันผลเด่น", desc: "High dividend yield focus" },
    //     { title: "กลุ่มเทคโนโลยี", desc: "AI and Next-Gen Tech" },
    //     { title: "กองทุนสุขภาพ", desc: "Global Healthcare megatrend" }
    // ];

    return (
        <main className="min-h-screen relative overflow-hidden bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-white transition-colors duration-300">
            <Navbar />

            {/* Background Decor */}
            <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary/20 dark:bg-primary/20 blur-[120px] rounded-full -z-10" />
            <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-accent/20 dark:bg-accent/20 blur-[120px] rounded-full -z-10" />

            {/* Content Section */}
            <section className="pt-32 pb-20 px-4">
                <div className="max-w-5xl mx-auto">
                    <div className="text-center mb-12">
                        <Title className="text-5xl md:text-6xl font-bold tracking-tight mb-4 text-slate-900 dark:text-white">
                            Discover <span className="text-gradient">Smart</span> Funds
                        </Title>
                        <Text className="text-lg md:text-xl text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
                            Navigate the complex market safely. Find the right funds using AI-powered insights and real-time sentiment analysis.
                        </Text>
                    </div>

                    <div className="glass bg-white/60 dark:bg-white/5 p-6 rounded-2xl shadow-xl dark:shadow-none mb-16 border border-slate-200 dark:border-white/10 max-w-3xl mx-auto transition-colors duration-300">
                        <FundSearchBox />
                    </div>

                    {/* <div className="flex items-center gap-4 mb-8">
                        <div className="h-px bg-white/10 flex-1" />
                        <span className="text-slate-500 font-medium uppercase tracking-wider text-sm">Trending Themes</span>
                        <div className="h-px bg-white/10 flex-1" />
                    </div> */}

                    {/* <Grid numItemsSm={2} numItemsLg={3} className="gap-6 mt-6">
                        {trendingThemes.map((theme, idx) => (
                            <Card 
                                key={idx} 
                                className="cursor-pointer transition-all duration-300 flex flex-col items-center text-center group glass hover:bg-white/8 hover:scale-105 border border-white/5 rounded-2xl p-6" 
                                onClick={() => { setSearchQuery(theme.title); document.querySelector('form')?.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true })); }}
                            >
                                <Title className="text-slate-200 group-hover:text-primary transition-colors text-xl font-bold">{theme.title}</Title>
                                <Text className="mt-3 text-slate-400">{theme.desc}</Text>
                            </Card>
                        ))}
                    </Grid> */}
                </div>
            </section>
        </main>
    );
}
