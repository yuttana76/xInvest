"use client";

import React from 'react';
import { FileText, Download, Calendar } from 'lucide-react';
import { Button } from '@/components/Button';

export default function OperatorReports() {
  const reports = [
    { title: "Monthly Registration Summary", desc: "overview of new investors joined this month", type: "PDF" },
    { title: "Compliance Status Report", desc: "List of investors with pending kyc or expired suitability", type: "Excel" },
    { title: "AUM Growth Analytic", desc: "Comparative analysis of Assets Under Management", type: "CSV" },
  ];

  return (
    <div className="text-slate-100">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">System Reports</h1>
        <p className="text-slate-400 mt-1">Generate and download data insights.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {reports.map((report, idx) => (
          <div key={idx} className="glass p-6 rounded-2xl border border-white/5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 group hover:border-white/10 transition-colors">
            <div className="flex items-center gap-4 min-w-0">
                <div className="p-3 rounded-xl bg-primary/10 text-primary shrink-0">
                    <FileText size={24} />
                </div>
                <div className="min-w-0">
                    <h3 className="font-semibold text-lg truncate">{report.title}</h3>
                    <p className="text-sm text-slate-500">{report.desc}</p>
                </div>
            </div>
            <div className="flex sm:flex-col items-center sm:items-end gap-2 shrink-0">
                <span className="text-xs font-mono text-slate-600 bg-white/5 px-2 py-1 rounded">{report.type}</span>
                <Button variant="outline" size="sm" className="opacity-100 sm:opacity-0 sm:group-hover:opacity-100 transition-opacity">
                    <Download size={16} className="mr-2" />
                    Download
                </Button>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-12 glass p-8 rounded-2xl border border-white/5 bg-linear-to-br from-primary/5 to-transparent">
        <div className="flex items-center gap-3 mb-4">
            <Calendar className="text-primary" size={24} />
            <h2 className="text-xl font-bold">Custom Report Builder</h2>
        </div>
        <p className="text-slate-400 mb-6 max-w-xl">
            Select a date range and data points to generate a custom export tailored to your requirements.
        </p>
        <div className="flex flex-col sm:flex-row sm:items-end gap-2 sm:gap-4">
            <Button disabled>Initialize Builder</Button>
            <span className="text-xs text-slate-600 sm:self-end sm:mb-1">Coming soon in version 2.0</span>
        </div>
      </div>
    </div>
  );
}
