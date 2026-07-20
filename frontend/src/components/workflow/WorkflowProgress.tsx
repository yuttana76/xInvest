import React, { useState } from 'react';
import { WorkflowRequest, ApprovalLog } from '@/lib/api/workflow';
import { Check, Clock, AlertCircle, XCircle, ChevronDown, ChevronUp } from 'lucide-react';
import { format } from 'date-fns';
import { enUS } from 'date-fns/locale';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface WorkflowProgressProps {
  request: WorkflowRequest;
}

const LogDetail: React.FC<{ log: ApprovalLog }> = ({ log }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const hasLongComment = log.comment && log.comment.length > 60;
  const displayComment = isExpanded ? log.comment : (hasLongComment ? `${log.comment.substring(0, 60)}...` : log.comment);

  return (
    <div className="mt-2 text-xs bg-gray-50 dark:bg-gray-800/50 p-3 rounded-lg border border-gray-100 dark:border-gray-700">
      <div className="flex justify-between items-start mb-1">
        <span className="font-bold text-gray-700 dark:text-gray-300">
          {log.action === 'APPROVE' && '✅ Approved'}
          {log.action === 'REJECT' && '❌ Rejected'}
          {log.action === 'RETURN' && '🔄 Returned'}
          {log.action === 'RESUBMIT' && '📤 Resubmitted'}
          by {log.approver_name || log.user_display}
        </span>
        <span className="text-gray-400">
          {format(new Date(log.created_at), 'd MMM HH:mm', { locale: enUS })}
        </span>
      </div>
      {log.comment && (
        <div className="text-gray-600 dark:text-gray-400 italic">
          &quot;{displayComment}&quot;
          {hasLongComment && (
            <button 
              onClick={() => setIsExpanded(!isExpanded)}
              className="ml-1 text-primary hover:underline font-medium inline-flex items-center gap-0.5"
            >
              {isExpanded ? (
                <>Show less <ChevronUp className="w-3 h-3" /></>
              ) : (
                <>Show more <ChevronDown className="w-3 h-3" /></>
              )}
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export const WorkflowProgress: React.FC<WorkflowProgressProps> = ({ request }) => {
  const { workflow_steps, current_step_number, status, logs } = request;

  if (!workflow_steps || workflow_steps.length === 0) return null;

  return (
    <div className="space-y-6">
      <div className="relative pl-8 space-y-10">
        {/* Vertical Line */}
        <div className="absolute left-[15px] top-2 bottom-2 w-0.5 bg-gray-200 dark:bg-gray-800" />

        {workflow_steps.map((step) => {
          const stepLogs = logs?.filter(l => l.step_number === step.step_number) || [];
          const isCompleted = step.step_number < current_step_number || status === 'COMPLETED' || (status === 'APPROVED' && step.step_number <= current_step_number);
          const isCurrent = step.step_number === current_step_number && status !== 'COMPLETED' && status !== 'REJECTED' && status !== 'RETURNED';
          const isRejected = status === 'REJECTED' && step.step_number === current_step_number;
          const isReturned = status === 'RETURNED' && step.step_number === current_step_number;

          return (
            <div key={step.id} className="relative flex flex-col group">
              <div className="flex items-start">
                {/* Node Icon */}
                <div className={cn(
                  "absolute -left-8 flex items-center justify-center w-8 h-8 rounded-full border-4 border-white dark:border-gray-900 z-10 transition-colors",
                  isCompleted ? "bg-green-500 text-white" : 
                  isCurrent ? "bg-primary text-white shadow-lg shadow-primary/30" : 
                  isRejected ? "bg-red-500 text-white" :
                  isReturned ? "bg-orange-500 text-white" :
                  "bg-gray-200 dark:bg-gray-800 text-gray-400"
                )}>
                  {isCompleted ? <Check className="w-4 h-4" /> : 
                   isCurrent ? <Clock className="w-4 h-4 animate-pulse" /> : 
                   isRejected ? <XCircle className="w-4 h-4" /> :
                   isReturned ? <AlertCircle className="w-4 h-4" /> :
                   <span className="text-xs font-bold">{step.step_number}</span>}
                </div>

                {/* Step Info */}
                <div className="ml-4 flex-1">
                  <div className="flex justify-between items-center">
                    <h4 className={cn(
                      "text-sm font-bold transition-colors",
                      isCompleted ? "text-green-600 dark:text-green-400" : 
                      isCurrent ? "text-primary" : 
                      isRejected ? "text-red-500" :
                      isReturned ? "text-orange-500" :
                      "text-gray-500"
                    )}>
                      {step.step_name}
                    </h4>
                    {isCurrent && (
                      <span className="text-[10px] font-bold uppercase py-0.5 px-2 bg-primary/10 text-primary rounded-full">
                        Waiting for Approval
                      </span>
                    )}
                  </div>
                  <span className="text-[11px] text-gray-400">
                    Reviewer Group: {step.required_group_name || 'Not specified'}
                  </span>
                  
                  {/* Step Logs */}
                  {stepLogs.length > 0 && (
                    <div className="space-y-2 mt-2">
                      {stepLogs.map(log => (
                        <LogDetail key={log.id} log={log} />
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}

        {/* Closing Step */}
        <div className="relative flex items-start group">
          <div className={cn(
            "absolute -left-8 flex items-center justify-center w-8 h-8 rounded-full border-4 border-white dark:border-gray-900 z-10 transition-colors",
            status === 'COMPLETED' ? "bg-emerald-500 text-white" : "bg-gray-200 dark:bg-gray-800 text-gray-400"
          )}>
            <Check className="w-4 h-4" />
          </div>
          <div className="ml-4 pt-1.5 flex flex-col justify-start">
            <h4 className={cn(
              "text-sm font-bold",
              status === 'COMPLETED' ? "text-emerald-600" : "text-gray-400"
            )}>
              Completed
            </h4>
            {status === 'COMPLETED' && (
               <span className="text-[11px] text-emerald-500 mt-1">
                 Operation completed successfully
               </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
