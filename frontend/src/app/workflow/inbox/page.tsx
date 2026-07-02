'use client';

import React, { useState } from 'react';
import { useWaitingApproval, useAllRequests, useWorkflowConfigs } from '@/hooks/useWorkflow';
import { WorkflowStatusBadge } from '@/components/workflow/WorkflowStatusBadge';
import { Button } from '@/components/Button';
import Link from 'next/link';
import { 
  Inbox, 
  Calendar, 
  User, 
  ArrowRight, 
  Clock, 
  ChevronLeft, 
  ChevronRight, 
  History, 
  CheckSquare, 
  Filter,
  AlertTriangle,
  ShieldCheck
} from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { format } from 'date-fns';
import { enUS } from 'date-fns/locale';

const PRIORITY_MAP: Record<number, { label: string; className: string }> = {
  1: { label: 'High',   className: 'bg-red-100 text-red-700 dark:bg-red-950/40 dark:text-red-400' },
  2: { label: 'Medium', className: 'bg-amber-100 text-amber-700 dark:bg-amber-950/40 dark:text-amber-400' },
  3: { label: 'Low',    className: 'bg-green-100 text-green-700 dark:bg-green-950/40 dark:text-green-400' },
};

export default function ApprovalInboxPage() {
  const [activeTab, setActiveTab] = useState<'pending' | 'history'>('pending');
  const [selectedWorkflow, setSelectedWorkflow] = useState<string>('all');
  const [currentPage, setCurrentPage] = useState<number>(1);
  const itemsPerPage = 10;

  const { user } = useAuth();
  const { data: requests, isLoading: isPendingLoading, error: pendingError } = useWaitingApproval();
  const { data: allRequests, isLoading: isAllLoading, error: allRequestsError } = useAllRequests();
  const { data: workflowConfigs } = useWorkflowConfigs();

  const isLoading = isPendingLoading || (activeTab === 'history' && isAllLoading);
  const error = pendingError || (activeTab === 'history' && allRequestsError);

  // Filter requests for history tab (only show requests the current user has approved or completed)
  const historyRequests = React.useMemo(() => {
    if (!allRequests || !user?.username) return [];
    return allRequests.filter(req => {
      const matchesWorkflow = selectedWorkflow === 'all' || req.workflow === Number(selectedWorkflow);
      if (!matchesWorkflow) return false;

      // Check if the current user has approved/completed this request in the logs
      const hasUserApproved = req.logs?.some(
        log => (log.action === 'APPROVE' || log.action === 'COMPLETE') && log.approver_username === user.username
      );
      return hasUserApproved;
    });
  }, [allRequests, selectedWorkflow, user]);

  // Handle tab switching (reset pagination)
  const handleTabChange = (tab: 'pending' | 'history') => {
    setActiveTab(tab);
    setCurrentPage(1);
  };

  // Handle workflow filter change (reset pagination)
  const handleWorkflowChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedWorkflow(e.target.value);
    setCurrentPage(1);
  };

  // Pagination for history
  const paginatedHistory = React.useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    return historyRequests.slice(startIndex, startIndex + itemsPerPage);
  }, [historyRequests, currentPage]);

  const totalPages = Math.ceil(historyRequests.length / itemsPerPage);

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
        <p className="text-red-600">Error loading data</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Approval Inbox</h1>
          <p className="text-sm text-gray-500 mt-1">
            {activeTab === 'pending'
              ? 'Requests waiting for your review and approval'
              : 'History of approved or completed requests'}
          </p>
        </div>
        {activeTab === 'pending' && (
          <div className="bg-primary/10 text-primary px-4 py-2 rounded-xl text-sm font-bold flex items-center self-start sm:self-auto">
            <Clock className="w-4 h-4 mr-2" />
            {requests?.length || 0} items pending
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200 dark:border-gray-800 gap-6">
        <button
          onClick={() => handleTabChange('pending')}
          className={`pb-4 text-sm font-semibold transition-all relative flex items-center gap-2 ${
            activeTab === 'pending'
              ? 'text-primary'
              : 'text-gray-500 hover:text-gray-900 dark:hover:text-white'
          }`}
        >
          <CheckSquare className="w-4.5 h-4.5" />
          Pending Approvals
          {requests && requests.length > 0 && (
            <span className="ml-1 bg-primary text-white text-xs px-2 py-0.5 rounded-full font-bold">
              {requests.length}
            </span>
          )}
          {activeTab === 'pending' && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary rounded-full" />
          )}
        </button>
        <button
          onClick={() => handleTabChange('history')}
          className={`pb-4 text-sm font-semibold transition-all relative flex items-center gap-2 ${
            activeTab === 'history'
              ? 'text-primary'
              : 'text-gray-500 hover:text-gray-900 dark:hover:text-white'
          }`}
        >
          <History className="w-4.5 h-4.5" />
          Approved History
          {activeTab === 'history' && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary rounded-full" />
          )}
        </button>
      </div>

      {/* Filters (only for History tab) */}
      {activeTab === 'history' && (
        <div className="flex items-center gap-3 bg-gray-50 dark:bg-white/5 p-4 rounded-2xl border border-gray-200 dark:border-white/10">
          <Filter className="w-4 h-4 text-gray-400 shrink-0" />
          <span className="text-xs font-semibold text-gray-500 dark:text-gray-400">Workflow Type:</span>
          <select
            value={selectedWorkflow}
            onChange={handleWorkflowChange}
            className="h-10 rounded-xl border border-gray-200 dark:border-white/10 bg-white dark:bg-white/5 px-3 py-1.5 text-sm focus:ring-2 focus:ring-primary/20 outline-none transition-all cursor-pointer text-gray-700 dark:text-gray-200"
          >
            <option value="all">All Workflows</option>
            {workflowConfigs?.map((cfg) => (
              <option key={cfg.id} value={cfg.id}>
                {cfg.name}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Main List */}
      <div className="grid grid-cols-1 gap-4">
        {activeTab === 'pending' ? (
          /* Pending Approvals Table */
          !requests || requests.length === 0 ? (
            <div className="bg-white dark:bg-gray-900 rounded-2xl border border-dashed border-gray-200 dark:border-gray-800 p-12 text-center text-gray-500">
              <Inbox className="w-16 h-16 mx-auto mb-4 opacity-10" />
              <p className="text-lg">Congratulations! No pending approvals at the moment.</p>
            </div>
          ) : (
            <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead className="bg-gray-50 dark:bg-gray-800/50 text-gray-500 uppercase font-semibold text-xs border-b border-gray-200 dark:border-gray-800">
                    <tr>
                      <th className="px-6 py-4">ID / Title</th>
                      <th className="px-6 py-4">Creator</th>
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
                    {requests.map((req) => (
                      <tr key={req.id} className="hover:bg-gray-50 dark:hover:bg-gray-800/30 transition-colors">
                        <td className="px-6 py-4">
                          <div className="font-medium text-gray-900 dark:text-white">
                            {req.req_code ? req.req_code : `#${req.id}`}
                          </div>
                          <div className="text-gray-500 text-xs truncate max-w-[200px]">{req.title}</div>
                        </td>
                        <td className="px-6 py-4 text-gray-600 dark:text-gray-400">
                          <div className="flex items-center text-xs">
                            <User className="w-3.5 h-3.5 mr-1.5 opacity-60" />
                            {req.creator_name && req.creator_name.trim() !== '' ? req.creator_name : req.creator_username}
                          </div>
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
                        {/* Current Step */}
                        <td className="px-6 py-4">
                          {req.status === 'PENDING' ? (
                            <div className="flex flex-col">
                              <span className="text-xs font-semibold text-primary">{req.current_step_info?.step_name}</span>
                              <span className="text-[10px] text-gray-400">Group: {req.current_step_info?.required_group_name}</span>
                            </div>
                          ) : (
                            <span className="text-xs text-gray-400">-</span>
                          )}
                        </td>
                        {/* Status */}
                        <td className="px-6 py-4">
                          <WorkflowStatusBadge status={req.status} />
                        </td>
                        {/* Date Created */}
                        <td className="px-6 py-4 text-gray-500 text-xs">
                          <div className="flex items-center">
                            <Calendar className="w-3 h-3 mr-1.5 opacity-60" />
                            {format(new Date(req.created_at), 'd MMM yyyy', { locale: enUS })}
                          </div>
                        </td>
                        {/* Audit */}
                        <td className="px-6 py-4 text-center">
                          {req.auditFlag && (
                            <ShieldCheck className="w-4 h-4 text-amber-500 mx-auto" />
                          )}
                        </td>
                        {/* Actions */}
                        <td className="px-6 py-4 text-right">
                          <Link href={`/workflow/requests/${req.id}`}>
                            <Button variant="primary" size="sm" className="rounded-full px-6">
                              Review
                              <ArrowRight className="w-4 h-4 ml-2" />
                            </Button>
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )
        ) : (
          /* Approved History Table */
          historyRequests.length === 0 ? (
            <div className="bg-white dark:bg-gray-900 rounded-2xl border border-dashed border-gray-200 dark:border-gray-800 p-12 text-center text-gray-500">
              <Inbox className="w-16 h-16 mx-auto mb-4 opacity-10" />
              <p className="text-lg">No approved workflows found.</p>
            </div>
          ) : (
            <>
              <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm">
                    <thead className="bg-gray-50 dark:bg-gray-800/50 text-gray-500 uppercase font-semibold text-xs border-b border-gray-200 dark:border-gray-800">
                      <tr>
                        <th className="px-6 py-4">ID / Title</th>
                        <th className="px-6 py-4">Creator</th>
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
                      {paginatedHistory.map((req) => (
                        <tr key={req.id} className="hover:bg-gray-50 dark:hover:bg-gray-800/30 transition-colors">
                          <td className="px-6 py-4">
                            <div className="font-medium text-gray-900 dark:text-white">
                              {req.req_code ? req.req_code : `#${req.id}`}
                            </div>
                            <div className="text-gray-500 text-xs truncate max-w-[200px]">{req.title}</div>
                          </td>
                          <td className="px-6 py-4 text-gray-600 dark:text-gray-400">
                            <div className="flex items-center text-xs">
                              <User className="w-3.5 h-3.5 mr-1.5 opacity-60" />
                              {req.creator_name && req.creator_name.trim() !== '' ? req.creator_name : req.creator_username}
                            </div>
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
                          {/* Current Step */}
                          <td className="px-6 py-4">
                            {req.status === 'PENDING' ? (
                              <div className="flex flex-col">
                                <span className="text-xs font-semibold text-primary">{req.current_step_info?.step_name}</span>
                                <span className="text-[10px] text-gray-400">Group: {req.current_step_info?.required_group_name}</span>
                              </div>
                            ) : req.status === 'APPROVED' ? (
                              <div className="flex flex-col">
                                <span className="text-xs font-bold text-emerald-600">Ready to Complete</span>
                                <span className="text-[10px] text-emerald-500/70">Ready for final execution</span>
                              </div>
                            ) : (
                              <span className="text-xs text-gray-400">-</span>
                            )}
                          </td>
                          {/* Status */}
                          <td className="px-6 py-4">
                            <WorkflowStatusBadge status={req.status} />
                          </td>
                          {/* Date Created */}
                          <td className="px-6 py-4 text-gray-500 text-xs">
                            <div className="flex items-center">
                              <Calendar className="w-3 h-3 mr-1.5 opacity-60" />
                              {format(new Date(req.created_at), 'd MMM yyyy', { locale: enUS })}
                            </div>
                          </td>
                          {/* Audit */}
                          <td className="px-6 py-4 text-center">
                            {req.auditFlag && (
                              <ShieldCheck className="w-4 h-4 text-amber-500 mx-auto" />
                            )}
                          </td>
                          {/* Actions */}
                          <td className="px-6 py-4 text-right">
                            <Link href={`/workflow/requests/${req.id}`}>
                              <Button variant="ghost" size="sm" className="text-primary hover:text-primary-dark">
                                Details
                                <ArrowRight className="w-3 h-3 ml-1.5" />
                              </Button>
                            </Link>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Pagination Controls */}
              {totalPages > 1 && (
                <div className="py-4 flex items-center justify-between border-t border-gray-100 dark:border-gray-800 mt-4">
                  <div className="text-sm text-gray-500">
                    Showing{' '}
                    <span className="font-semibold text-gray-800 dark:text-gray-200">
                      {(currentPage - 1) * itemsPerPage + 1}
                    </span>{' '}
                    to{' '}
                    <span className="font-semibold text-gray-800 dark:text-gray-200">
                      {Math.min(currentPage * itemsPerPage, historyRequests.length)}
                    </span>{' '}
                    of{' '}
                    <span className="font-semibold text-gray-800 dark:text-gray-200">
                      {historyRequests.length}
                    </span>{' '}
                    records
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={currentPage === 1}
                      onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
                    >
                      <ChevronLeft className="w-4 h-4" />
                    </Button>
                    <div className="flex items-center gap-1">
                      {Array.from({ length: totalPages }, (_, i) => {
                        const pageNum = i + 1;
                        if (
                          pageNum === 1 ||
                          pageNum === totalPages ||
                          Math.abs(pageNum - currentPage) <= 1
                        ) {
                          return (
                            <Button
                              key={pageNum}
                              variant={currentPage === pageNum ? 'primary' : 'ghost'}
                              size="sm"
                              className="w-8 h-8 p-0"
                              onClick={() => setCurrentPage(pageNum)}
                            >
                              {pageNum}
                            </Button>
                          );
                        }
                        if (
                          pageNum === 2 ||
                          pageNum === totalPages - 1
                        ) {
                          return <span key={pageNum} className="text-gray-400 px-1">...</span>;
                        }
                        return null;
                      })}
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={currentPage === totalPages}
                      onClick={() => setCurrentPage((prev) => Math.min(totalPages, prev + 1))}
                    >
                      <ChevronRight className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              )}
            </>
          )
        )}
      </div>
    </div>
  );
}
