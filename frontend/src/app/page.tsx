import React from 'react';
import { Navbar } from '@/components/Navbar';
import { Button } from '@/components/Button';
import { FundSearchBox } from '@/components/FundSearchBox';
import Link from 'next/link';

export default function LandingPage() {
  return (
    <main className="min-h-screen relative overflow-hidden bg-white dark:bg-slate-950 transition-colors duration-300">
      <Navbar />

      {/* Background Decor */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary/20 blur-[120px] rounded-full -z-10" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-accent/20 blur-[120px] rounded-full -z-10" />

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4">
        <div className="max-w-7xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 mb-8">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
            </span>
            <span className="text-xs font-medium text-slate-600 dark:text-slate-300">New: AI Portfolio Rebalancing v2.0</span>
          </div>

          <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6 text-slate-900 dark:text-white">
            Smart Portfolios, <br />
            <span className="text-gradient">Driven by Intelligence</span>
          </h1>
          <p className="max-w-2xl mx-auto text-lg md:text-xl text-slate-600 dark:text-slate-400 mb-10">
            The next generation of investment management. Optimize your assets with advanced Sharpe Ratio algorithms and real-time market insights.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-12">
            <Link href="/register"><Button size="lg">Start Investing Now</Button></Link>
            <Button variant="outline" size="lg">Watch Demo</Button>
          </div>

          <div className="max-w-3xl mx-auto p-4 glass rounded-2xl border border-slate-200 dark:border-white/10 shadow-2xl">
            <FundSearchBox placeholder="Try searching Fund to see insights in action..." />
          </div>

          {/* Hero Mockup */}
          {/* <div className="mt-20 relative">
            <div className="glass rounded-2xl p-4 md:p-8 max-w-5xl mx-auto shadow-2xl">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {[
                  { label: "Portfolio Value", value: "$124,592.00", change: "+12.4%", color: "text-primary" },
                  { label: "Sharpe Ratio", value: "2.45", change: "Excellent", color: "text-secondary" },
                  { label: "Daily Return", value: "+$1,240.50", change: "+1.05%", color: "text-accent" }
                ].map((stat, i) => (
                  <div key={i} className="bg-white/5 rounded-xl p-6 text-left border border-white/5">
                    <p className="text-sm text-slate-400 mb-1">{stat.label}</p>
                    <h3 className="text-2xl font-bold mb-1">{stat.value}</h3>
                    <p className={`text-sm font-medium ${stat.color}`}>{stat.change}</p>
                  </div>
                ))}
              </div>
              <div className="mt-8 h-64 md:h-96 w-full bg-white/5 rounded-xl border border-white/5 flex items-center justify-center relative overflow-hidden">
                <div className="absolute inset-x-0 bottom-0 h-48 bg-linear-to-t from-primary/10 to-transparent" />
                <span className="text-slate-500 font-medium">Interactive Performance Chart Coming Soon</span>
              </div>
            </div>
          </div> */}

        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 px-4 bg-slate-50/50 dark:bg-white/2">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4 text-slate-900 dark:text-white">Powerful Features for Serious Investors</h2>
            <p className="text-slate-600 dark:text-slate-400">Everything you need to outperform the market, all in one place.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                title: "Sharpe Optimization",
                desc: "Balance risk and reward perfectly using our proprietary Modern Portfolio Theory engine.",
                icon: "📈"
              },
              {
                title: "Real-time Tracking",
                desc: "Get sub-second updates on your assets across global markets and exchanges.",
                icon: "⚡"
              },
              {
                title: "Smart Rebalancing",
                desc: "Automatic alerts and execution when your portfolio drifts from your target allocation.",
                icon: "⚖️"
              }
            ].map((feature, i) => (
              <div key={i} className="p-8 rounded-2xl glass border border-slate-200 dark:border-white/5 hover:bg-slate-50 dark:hover:bg-white/5 transition-colors group">
                <div className="text-4xl mb-4 grayscale group-hover:grayscale-0 transition-all">{feature.icon}</div>
                <h3 className="text-xl font-bold mb-2 text-slate-800 dark:text-white">{feature.title}</h3>
                <p className="text-slate-600 dark:text-slate-400 leading-relaxed">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t border-slate-200 dark:border-white/5 px-4 text-center">
        <div className="flex items-center justify-center gap-2 mb-4 opacity-50">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-primary rounded flex items-center justify-center">
              <span className="text-white font-bold text-sm">x</span>
            </div>
            <span className="text-lg font-bold tracking-tight text-slate-900 dark:text-white">Invest</span>
          </div>
        </div>
        <p className="text-sm text-slate-500">
          © 2026 xInvest Technologies. All rights reserved. <br className="md:hidden" />
          <span className="hidden md:inline"> | </span>
          Smart Investing for Everyone.
        </p>
      </footer>
    </main>
  );
}
