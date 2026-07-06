import React from 'react';
import { Navbar } from '@/components/Navbar';
import { Button } from '@/components/Button';
import Link from 'next/link';
import { APP_NAME, APP_NAME_BADGE, APP_NAME_REST } from '@/lib/branding';
import {
  ListChecks,
  Workflow as WorkflowIcon,
  ShieldCheck,
  Inbox,
  Paperclip,
  History,
  ArrowRight,
} from 'lucide-react';

const STEPS = [
  {
    step: '01',
    title: 'Submit a Request',
    desc: 'Raise a request from any department — IT, purchasing, HR, or finance — with details, priority, and file attachments.',
    icon: ListChecks,
  },
  {
    step: '02',
    title: 'Auto-Routed for Approval',
    desc: 'Configurable approval chains route each request to the right approver, in the right order, automatically.',
    icon: WorkflowIcon,
  },
  {
    step: '03',
    title: 'Review & Decide',
    desc: 'Approvers review, approve, reject, or return requests with comments — all from a single inbox.',
    icon: Inbox,
  },
  {
    step: '04',
    title: 'Tracked to Completion',
    desc: 'Every action is logged to a full audit trail, so status and history are always one click away.',
    icon: History,
  },
];

const FEATURES = [
  {
    title: 'Configurable Approval Steps',
    desc: 'Define multi-level approval chains per workflow type, so every request follows the right process without manual routing.',
    icon: WorkflowIcon,
  },
  {
    title: 'Role-Based Inbox',
    desc: 'Approvers see only what needs their action — pending requests, priorities, and due dates in one clear view.',
    icon: Inbox,
  },
  {
    title: 'Full Audit Trail',
    desc: 'Every submission, approval, rejection, and comment is timestamped and logged for compliance and accountability.',
    icon: History,
  },
  {
    title: 'Attachments Built In',
    desc: 'Attach supporting files directly to a request so approvers have everything they need to decide, in context.',
    icon: Paperclip,
  },
  {
    title: 'Real-Time Status Tracking',
    desc: 'Requesters can track progress at every step — pending, in progress, returned, approved, or completed.',
    icon: ListChecks,
  },
  {
    title: 'Enterprise-Ready Controls',
    desc: 'Role-based access and structured approval logs keep company processes consistent, secure, and auditable.',
    icon: ShieldCheck,
  },
];

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
            <span className="text-xs font-medium text-slate-600 dark:text-slate-300">New: Multi-Level Approval Automation</span>
          </div>

          <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6 text-slate-900 dark:text-white">
            Company Workflows, <br />
            <span className="text-gradient">Approved Without the Chaos</span>
          </h1>
          <p className="max-w-2xl mx-auto text-lg md:text-xl text-slate-600 dark:text-slate-400 mb-10">
            One platform to submit, route, and approve requests across every department — with configurable approval
            chains, a role-based inbox, and a full audit trail for every decision.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-12">
            <Link href="/workflow/create"><Button size="lg">Create a Request</Button></Link>
            <Link href="/workflow/inbox"><Button variant="outline" size="lg">Go to Approval Inbox</Button></Link>
          </div>

          {/* Hero Mockup: mini workflow preview */}
          <div className="max-w-4xl mx-auto p-4 md:p-8 glass rounded-2xl border border-slate-200 dark:border-white/10 shadow-2xl">
            <div className="flex flex-col md:flex-row items-stretch gap-4 text-left">
              {STEPS.map((s, i) => (
                <React.Fragment key={s.step}>
                  <div className="flex-1 rounded-xl p-5 bg-white/60 dark:bg-white/5 border border-slate-200 dark:border-white/5">
                    <div className="flex items-center gap-2 mb-3">
                      <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                        <s.icon className="w-4 h-4 text-primary" />
                      </div>
                      <span className="text-xl font-semibold text-slate-400">{s.step}</span>
                    </div>
                    <h3 className="text-sm font-bold text-slate-800 dark:text-white mb-1">{s.title}</h3>
                    <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">{s.desc}</p>
                  </div>
                  {i < STEPS.length - 1 && (
                    <div className="hidden md:flex items-center justify-center text-slate-300 dark:text-slate-700">
                      <ArrowRight className="w-5 h-5" />
                    </div>
                  )}
                </React.Fragment>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 px-4 bg-slate-50/50 dark:bg-white/2">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4 text-slate-900 dark:text-white">Built for Every Team&apos;s Approval Process</h2>
            <p className="text-slate-600 dark:text-slate-400">From IT tickets to purchase orders — one consistent workflow engine, company-wide.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {FEATURES.map((feature, i) => (
              <div key={i} className="p-8 rounded-2xl glass border border-slate-200 dark:border-white/5 hover:bg-slate-50 dark:hover:bg-white/5 transition-colors group">
                <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center mb-4 group-hover:bg-primary/20 transition-colors">
                  <feature.icon className="w-6 h-6 text-primary" />
                </div>
                <h3 className="text-xl font-bold mb-2 text-slate-800 dark:text-white">{feature.title}</h3>
                <p className="text-slate-600 dark:text-slate-400 leading-relaxed">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4">
        <div className="max-w-4xl mx-auto text-center glass rounded-2xl border border-slate-200 dark:border-white/10 shadow-xl p-12">
          <h2 className="text-2xl md:text-3xl font-bold mb-3 text-slate-900 dark:text-white">Bring order to your company&apos;s approvals</h2>
          <p className="text-slate-600 dark:text-slate-400 mb-8">
            Set up a workflow once, then let every request move through it — tracked, logged, and accountable.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/register"><Button size="lg">Get Started</Button></Link>
            <Link href="/workflow/my-requests"><Button variant="outline" size="lg">View My Requests</Button></Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t border-slate-200 dark:border-white/5 px-4 text-center">
        <div className="flex items-center justify-center gap-2 mb-4 opacity-50">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-primary rounded flex items-center justify-center">
              <span className="text-white font-bold text-sm">{APP_NAME_BADGE}</span>
            </div>
            <span className="text-lg font-bold tracking-tight text-slate-900 dark:text-white">{APP_NAME_REST}</span>
          </div>
        </div>
        <p className="text-sm text-slate-500">
          © 2026 {APP_NAME} Technologies. All rights reserved. <br className="md:hidden" />
          <span className="hidden md:inline"> | </span>
          Workflow Automation for Modern Teams.
        </p>
      </footer>
    </main>
  );
}
