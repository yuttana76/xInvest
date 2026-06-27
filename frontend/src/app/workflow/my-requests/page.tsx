'use client';

import React from 'react';
import { useMyRequests } from '@/hooks/useWorkflow';
import { WorkflowStatusBadge } from '@/components/workflow/WorkflowStatusBadge';
import { Button } from '@/components/Button';
import Link from 'next/link';
import { Plus, FileText, Calendar, ArrowRight, AlertTriangle, ShieldCheck } from 'lucide-react';
import { format } from 'date-fns';
import { enUS } from 'date-fns/locale';

const PRIORITY_MAP: Record<number, { label: string; className: string }> = {
  1: { label: 'High',   className: 'bg-red-100 text-red-700 dark:bg-red-950/40 dark:text-red-400' },
  2: { label: 'Medium', className: 'bg-amber-100 text-amber-700 dark:bg-amber-950/40 dark:text-amber-400' },
  3: { label: 'Low',    className: 'bg-green-100 text-green-700 dark:bg-green-950/40 dark:text-green-400' },
};

export default function MyRequestsPage() {
  const { data: requests, isLoading, error } = useMyRequests();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 text-center bg-red-50 dark:bg-red-900/10 rounded-xl border border-red-100 dark:border-red-900/20">
        <p className="text-red-600 dark:text-red-400">Error loading your requests</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">My Requests</h1>
          <p className="text-sm text-gray-500 mt-1">Track the status and history of all requests you created</p>
        </div>
        <Link href="/workflow/create">
          <Button className="w-full sm:w-auto">
            <Plus className="w-4 h-4 mr-2" />
            Create New Request
          </Button>
        </Link>
      </div>

      <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-gray-50 dark:bg-gray-800/50 text-gray-500 uppercase font-semibold text-xs border-b border-gray-200 dark:border-gray-800">
              <tr>
                <th className="px-6 py-4">ID / Title</th>
                <th className="px-6 py-4">Workflow Type</th>
                <th className="px-6 py-4">Priority</th>
                <th className="px-6 py-4">Current Step</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4">Date Created</th>
                <th className="px-6 py-4">Audit</th>
                <th className="px-6 py-4"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
              {requests?.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-6 py-12 text-center text-gray-500 italic">
                    <FileText className="w-12 h-12 mx-auto mb-3 opacity-20" />
                    You don&apos;t have any requests at the moment.
                  </td>
                </tr>
              ) : (
                requests?.map((req) => (
                  <tr key={req.id} className="hover:bg-gray-50 dark:hover:bg-gray-800/30 transition-colors">
                    <td className="px-6 py-4">
                      <div className="font-medium text-gray-900 dark:text-white">
                        {req.req_code ? req.req_code : `#${req.id}`}
                      </div>
                      <div className="text-gray-500 text-xs truncate max-w-[200px]">{req.title}</div>
                    </td>
                    <td className="px-6 py-4 text-gray-600 dark:text-gray-400">
                      {req.workflow_name}
                    </td>
                    {/* Priority */}
                    <td className="px-6 py-4">
                      {(() => {
                        const p = PRIORITY_MAP[req.priorify] ?? PRIORITY_MAP[2];
                        return (
                          <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold ${p.className}`}>
                            <AlertTriangle className="w-3 h-3" />
                            {p.label}
                          </span>
                        );
                      })()}
                    </td>
                    <td className="px-6 py-4">
                      {req.status === 'PENDING' ? (
                        <div className="flex flex-col">
                          <span className="text-xs font-semibold text-primary">{req.current_step_info?.step_name}</span>
                          <span className="text-[10px] text-gray-400">Group: {req.current_step_info?.required_group_name}</span>
                        </div>
                      ) : req.status === 'APPROVED' ? (
                        <div className="flex flex-col">
                          <span className="text-xs font-bold text-emerald-600">Ready to Complete</span>
                          <span className="text-[10px] text-emerald-500/70">You can now complete the task</span>
                        </div>
                      ) : (
                        <span className="text-xs text-gray-400">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <WorkflowStatusBadge status={req.status} />
                    </td>
                    <td className="px-6 py-4 text-gray-500 text-xs">
                      <div className="flex items-center">
                        <Calendar className="w-3 h-3 mr-1.5 opacity-60" />
                        {format(new Date(req.created_at), 'd MMM yyyy', { locale: enUS })}
                      </div>
                    </td>
                    {/* Audit */}
                    <td className="px-6 py-4 text-center">
                      {req.auditFlag && (
                        <ShieldCheck className="w-4 h-4 text-amber-500 mx-auto" title="Audit Case" />
                      )}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <Link href={`/workflow/requests/${req.id}`}>
                        <Button variant="ghost" size="sm" className="text-primary hover:text-primary-dark">
                          Details
                          <ArrowRight className="w-3 h-3 ml-1.5" />
                        </Button>
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
