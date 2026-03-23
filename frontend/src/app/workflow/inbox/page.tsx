'use client';

import React from 'react';
import { useWaitingApproval } from '@/hooks/useWorkflow';
import { WorkflowStatusBadge } from '@/components/workflow/WorkflowStatusBadge';
import { Button } from '@/components/Button';
import Link from 'next/link';
import { Inbox, Calendar, User, ArrowRight, Clock } from 'lucide-react';
import { format } from 'date-fns';
import { enUS } from 'date-fns/locale';

export default function ApprovalInboxPage() {
  const { data: requests, isLoading, error } = useWaitingApproval();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 text-center bg-red-50 dark:bg-red-900/10 rounded-xl">
        <p className="text-red-600">Error loading approval list</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Approval Inbox</h1>
          <p className="text-sm text-gray-500 mt-1">Requests waiting for your review and approval</p>
        </div>
        <div className="bg-primary/10 text-primary px-4 py-2 rounded-xl text-sm font-bold flex items-center">
          <Clock className="w-4 h-4 mr-2" />
          {requests?.length || 0} items pending
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {requests?.length === 0 ? (
          <div className="bg-white dark:bg-gray-900 rounded-2xl border border-dashed border-gray-200 dark:border-gray-800 p-12 text-center text-gray-500">
            <Inbox className="w-16 h-16 mx-auto mb-4 opacity-10" />
            <p className="text-lg">Congratulations! No pending approvals at the moment.</p>
          </div>
        ) : (
          requests?.map((req) => (
            <div 
              key={req.id} 
              className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 p-5 shadow-sm hover:shadow-md transition-all group"
            >
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="space-y-1 flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono text-gray-400 bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded">
                      {req.req_code ? req.req_code : `#${req.id}`}
                    </span>
                    <h3 className="font-bold text-gray-900 dark:text-white group-hover:text-primary transition-colors">{req.title}</h3>
                  </div>
                  <div className="flex flex-wrap items-center gap-y-1 gap-x-4 text-xs text-gray-500">
                    <span className="flex items-center">
                      <User className="w-3.5 h-3.5 mr-1.5 opacity-60" />
                      {req.creator_name}
                    </span>
                    <span className="flex items-center">
                      <Calendar className="w-3.5 h-3.5 mr-1.5 opacity-60" />
                      {format(new Date(req.created_at), 'd MMM yyyy HH:mm', { locale: enUS })}
                    </span>
                    <span className="text-primary/80 font-medium">
                      {req.workflow_name}
                    </span>
                  </div>
                </div>
                
                <div className="flex items-center justify-between md:justify-end gap-4 border-t md:border-t-0 pt-4 md:pt-0 mt-2 md:mt-0">
                  <WorkflowStatusBadge status={req.status} />
                  <Link href={`/workflow/requests/${req.id}`}>
                    <Button variant="primary" size="sm" className="rounded-full px-6">
                      Review
                      <ArrowRight className="w-4 h-4 ml-2" />
                    </Button>
                  </Link>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
