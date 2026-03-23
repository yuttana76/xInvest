'use client';

import React from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useRequestDetail, useWaitingApproval } from '@/hooks/useWorkflow';
import { useAuth } from '@/hooks/useAuth';
import { WorkflowStatusBadge } from '@/components/workflow/WorkflowStatusBadge';
import { WorkflowProgress } from '@/components/workflow/WorkflowProgress';
import { ActionPanel } from '@/components/workflow/ActionPanel';
import { ResubmitForm } from '@/components/workflow/ResubmitForm';
import { RatingForm } from '@/components/workflow/RatingForm';
import { Button } from '@/components/Button';
import { ChevronLeft, FileText, Download, User, Layout } from 'lucide-react';

export default function RequestDetailPage() {
  const { id } = useParams();
  const router = useRouter();
  const requestId = parseInt(id as string);
  const { user } = useAuth();

  const { data: request, isLoading, error } = useRequestDetail(requestId);
  const { data: waitingList } = useWaitingApproval();

  const isApprover = waitingList?.some((req) => req.id === requestId);
  const isCreator = request?.creator_username?.toLowerCase().trim() === user?.username?.toLowerCase().trim();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
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

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Button variant="ghost" size="icon" onClick={() => router.back()}>
            <ChevronLeft className="w-5 h-5" />
          </Button>
          <h1 className="text-2xl font-bold">Request Details {request.req_code ? request.req_code : `#${request.id}`}</h1>
        </div>
        <WorkflowStatusBadge status={request.status} className="px-4 py-1.5 text-sm" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 p-6 shadow-sm">
            <h2 className="text-xl font-bold mb-4">{request.title}</h2>
            
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
                   {request.creator_name}
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

            <div className="prose dark:prose-invert max-w-none text-gray-700 dark:text-gray-300">
              <p className="whitespace-pre-wrap">{request.description}</p>
            </div>

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
                      <span className="text-xs font-medium truncate max-w-[150px]">{file.filename}</span>
                      <Download className="w-4 h-4 text-gray-400 group-hover:text-primary transition-colors" />
                    </a>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Conditional: Resubmit Form */}
          {isCreator && request.status === 'RETURNED' && (
            <ResubmitForm request={request} />
          )}

          {/* Conditional: Action Panel */}
          {((isApprover && request.status === 'PENDING') || (isCreator && request.status === 'APPROVED')) && (
            <ActionPanel requestId={request.id} status={request.status} />
          )}
          {/* Conditional: Rating Form */}
          {request.status === 'COMPLETED' && (
            <RatingForm request={request} isCreator={isCreator} />
          )}
        </div>

        {/* Sidebar: System Journey */}
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
