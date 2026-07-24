'use client';

import React, { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useRequestDetail, useWaitingApproval } from '@/hooks/useWorkflow';
import { useAuth } from '@/hooks/useAuth';
import { workflowApi } from '@/lib/api/workflow';
import { WorkflowStatusBadge } from '@/components/workflow/WorkflowStatusBadge';
import { WorkflowProgress } from '@/components/workflow/WorkflowProgress';
import { ActionPanel } from '@/components/workflow/ActionPanel';
import { ResubmitForm } from '@/components/workflow/ResubmitForm';
import { RatingForm } from '@/components/workflow/RatingForm';
import { Button } from '@/components/Button';
import {
  ChevronLeft, FileText, Download, User, Layout,
  Tag, AlertTriangle, CalendarClock, ShieldCheck, FileDown,
} from 'lucide-react';

// ── helpers ──────────────────────────────────────────────────────────────────
const PRIORITY_MAP: Record<number, { label: string; className: string }> = {
  1: { label: 'High',   className: 'bg-red-100 text-red-700 dark:bg-red-950/40 dark:text-red-400' },
  2: { label: 'Medium', className: 'bg-amber-100 text-amber-700 dark:bg-amber-950/40 dark:text-amber-400' },
  3: { label: 'Low',    className: 'bg-green-100 text-green-700 dark:bg-green-950/40 dark:text-green-400' },
};

function formatDate(iso: string | null | undefined) {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('th-TH', {
    year: 'numeric', month: 'short', day: 'numeric',
  });
}

// ── IT request meta card ──────────────────────────────────────────────────────
function ITRequestMeta({ request }: { request: ReturnType<typeof useRequestDetail>['data'] }) {
  if (!request) return null;

  const subjects  = request.reqSubject_details ?? [];

  return (
    <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 p-6 shadow-sm">
      {/* <h3 className="text-sm font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400 mb-4">
        IT Request Details
      </h3> */}

    <h3 className="text-xl font-bold mb-4">{request.title}</h3>
      <div className="prose dark:prose-invert max-w-none text-gray-700 dark:text-gray-300">
              <p className="whitespace-pre-wrap">{request.description}</p>
        </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-6">
        {/* Subject(s) */}
        <div className="sm:col-span-2">
          <div className="flex items-center gap-1.5 text-xs text-gray-500 mb-2">
            <Tag className="w-3.5 h-3.5" /> Subject(s)
          </div>
          {subjects.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {subjects.map((s) => (
                <span
                  key={s.id}
                  className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-700 dark:bg-blue-950/40 dark:text-blue-300"
                >
                  {s.name}
                </span>
              ))}
            </div>
          ) : (
            <span className="text-sm text-gray-400 italic">No subjects selected</span>
          )}
        </div>

        {/* Priority */}
        {/* <div>
          <div className="flex items-center gap-1.5 text-xs text-gray-500 mb-2">
            <AlertTriangle className="w-3.5 h-3.5" /> Priority
          </div>
          <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold ${priority.className}`}>
            {priority.label}
          </span>
        </div> */}
        {/* Expected Date */}
        {/* <div>
          <div className="flex items-center gap-1.5 text-xs text-gray-500 mb-2">
            <CalendarClock className="w-3.5 h-3.5" /> Expected Completion
          </div>
          <span className="text-sm font-medium text-gray-800 dark:text-gray-200">
            {formatDate(request.expectDate)}
          </span>
        </div> */}

        {/* Audit Flag */}
        {/* <div className="sm:col-span-2">
          <div className="flex items-center gap-1.5 text-xs text-gray-500 mb-2">
            <ShieldCheck className="w-3.5 h-3.5" /> Audit Case
          </div>
          {request.auditFlag ? (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-100 text-amber-700 dark:bg-amber-950/40 dark:text-amber-400">
              <ShieldCheck className="w-3.5 h-3.5" /> Marked as Audit Case
            </span>
          ) : (
            <span className="text-sm text-gray-400">Not an audit case</span>
          )}
        </div> */}
        
      </div>
    </div>
  );
}

// ── page ─────────────────────────────────────────────────────────────────────
export default function RequestDetailPage() {
  const { id } = useParams();
  const router  = useRouter();
  const requestId = parseInt(id as string);
  const { user }  = useAuth();

  const { data: request, isLoading, error } = useRequestDetail(requestId);
  const { data: waitingList } = useWaitingApproval();
  const [isExporting, setIsExporting] = useState(false);

  const isApprover = waitingList?.some((req) => req.id === requestId);
  const isCreator  = request?.creator_username?.toLowerCase().trim() === user?.username?.toLowerCase().trim();

  const handleExportPdf = async () => {
    if (!request) return;
    setIsExporting(true);
    try {
      const blob = await workflowApi.exportPdf(request.id);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${request.req_code || request.id}_WFreport.pdf`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to export PDF:', err);
      alert('Failed to export PDF. This export is only available for IT Request workflows.');
    } finally {
      setIsExporting(false);
    }
  }; 

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
      </div>
    );
  }

  if (error || !request) {
    return (
      <div className="p-8 text-center bg-red-50 dark:bg-red-900/10 rounded-xl">
        <p className="text-red-600">Request not found or an error occurred</p>
        <Button variant="outline" className="mt-4" onClick={() => router.back()}>
          Go back
        </Button>
      </div>
    );
  }

  const priority = PRIORITY_MAP[request.priorify] ?? PRIORITY_MAP[2];

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center space-x-2 min-w-0">
          <Button variant="ghost" size="icon" onClick={() => router.back()}>
            <ChevronLeft className="w-5 h-5" />
          </Button>
          <h1 className="text-2xl font-bold break-words">
            Request Details {request.req_code ? request.req_code : `#${request.id}`}
          </h1>
        </div>
        <div className="flex flex-wrap items-center gap-2 self-start sm:self-auto">
          {request.workflow_category === 'IT' && (
            <Button
              variant="outline"
              size="sm"
              onClick={handleExportPdf}
              disabled={isExporting}
            >
              <FileDown className="w-4 h-4 mr-2" />
              {isExporting ? 'Exporting...' : 'Export PDF'}
            </Button>
          )}
          <WorkflowStatusBadge status={request.status} className="px-4 py-1.5 text-sm" />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* ── Main Content ── */}
        <div className="lg:col-span-2 space-y-6">
          {/* General info */}
          <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 p-6 shadow-sm">
            {/* <h3 className="text-xl font-bold mb-4">{request.title}</h3> */}

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
              <div className="bg-gray-50 dark:bg-gray-800/50 p-3 rounded-xl border border-gray-100 dark:border-gray-800">
                <span className="text-xs text-gray-500 block mb-1">Workflow Type</span>
                <span className="text-sm font-medium flex items-center">
                  <Layout className="w-3.5 h-3.5 mr-1.5 opacity-60" />
                  {request.workflow_name}
                </span>
              </div>
              <div className="bg-gray-50 dark:bg-gray-800/50 p-3 rounded-xl border border-gray-100 dark:border-gray-800">
                <span className="text-xs text-gray-500 block mb-1">Created By</span>
                <span className="text-sm font-medium flex items-center">
                  <User className="w-3.5 h-3.5 mr-1.5 opacity-60" />
                  {request.creator_name && request.creator_name.trim() !== '' ? request.creator_name : request.creator_username}
                </span>
              </div>
              <div className="bg-gray-50 dark:bg-gray-800/50 p-3 rounded-xl border border-gray-100 dark:border-gray-800">
                <span className="text-xs text-gray-500 block mb-1">Department</span>
                <span className="text-sm font-medium flex items-center">
                  <Layout className="w-3.5 h-3.5 mr-1.5 opacity-60" />
                  {request.create_department || 'N/A'}
                </span>
              </div>
            </div>

            {/* <div className="prose dark:prose-invert max-w-none text-gray-700 dark:text-gray-300">
              <p className="whitespace-pre-wrap">{request.description}</p>
            </div> */}


    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* Priority */}
        <div>
          <div className="flex items-center gap-1.5 text-xs text-gray-500 mb-2">
            <AlertTriangle className="w-3.5 h-3.5" /> Priority
          </div>
          <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold ${priority.className}`}>
            {priority.label}
          </span>
        </div>
        {/* Expected Date */}
        <div>
          <div className="flex items-center gap-1.5 text-xs text-gray-500 mb-2">
            <CalendarClock className="w-3.5 h-3.5" /> Expected Completion
          </div>
          <span className="text-sm font-medium text-gray-800 dark:text-gray-200">
            {formatDate(request.expectDate)}
          </span>
        </div>

        {/* Audit Flag */}
        <div className="sm:col-span-2">
          <div className="flex items-center gap-1.5 text-xs text-gray-500 mb-2">
            <ShieldCheck className="w-3.5 h-3.5" /> Audit Case
          </div>
          {request.auditFlag ? (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-100 text-amber-700 dark:bg-amber-950/40 dark:text-amber-400">
              <ShieldCheck className="w-3.5 h-3.5" /> Marked as Audit Case
            </span>
          ) : (
            <span className="text-sm text-gray-400">Not an audit case</span>
          )}
        </div>
        
      </div>

        {/* ── IT Request Details ── */}
          <ITRequestMeta request={request} />

            {/* Attachments */}
            {request.files && request.files.length > 0 && (
              <div className="mt-8 pt-6 border-t border-gray-100 dark:border-gray-800">
                <h3 className="text-sm font-semibold mb-3 flex items-center">
                  <FileText className="w-4 h-4 mr-2" />
                  Attachments ({request.files.length})
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {request.files.map((file) => (
                    <a
                      key={file.id}
                      href={file.file}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center justify-between p-3 rounded-xl border border-gray-200 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors group"
                    >
                      <div className="flex items-center space-x-2 min-w-0">
                        <FileText className="w-4 h-4 text-gray-400 flex-shrink-0" />
                        <span
                          className="text-xs font-medium truncate max-w-[200px] md:max-w-[300px]"
                          title={file.file_name || file.filename || file.file.split('/').pop()}
                        >
                          {file.file_name || file.filename || file.file.split('/').pop()}
                        </span>
                      </div>
                      <Download className="w-4 h-4 text-gray-400 group-hover:text-primary transition-colors flex-shrink-0 ml-2" />
                    </a>
                  ))}
                </div>
              </div>
            )}
          </div>

          

          {/* Resubmit Form */}
          {isCreator && request.status === 'RETURNED' && (
            <ResubmitForm request={request} />
          )}

          {/* Action Panel (approver approve/reject/return OR creator complete) */}
          {((isApprover && request.status === 'PENDING') || (isCreator && request.status === 'APPROVED')) && (
            <ActionPanel requestId={request.id} status={request.status} />
          )}

          {/* Rating Form */}
          {request.status === 'COMPLETED' && (
            <RatingForm request={request} isCreator={isCreator} />
          )}
        </div>

        {/* ── Sidebar: Progress ── */}
        <div className="space-y-6">
          <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 p-6 shadow-sm">
            <h2 className="text-sm font-bold uppercase tracking-wider text-gray-500 mb-8 font-mono pb-4 border-b border-gray-100 dark:border-gray-800">
              Progress (Request Journey)
            </h2>
            <WorkflowProgress request={request} />
          </div>
        </div>
      </div>
    </div>
  );
}
