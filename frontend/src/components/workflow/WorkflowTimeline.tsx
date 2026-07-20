import React from 'react';
import { ApprovalLog } from '@/lib/api/workflow';
import { CheckCircle2, XCircle, RotateCcw, Send, PlayCircle, Flag } from 'lucide-react';
import { format } from 'date-fns';
import { enUS } from 'date-fns/locale';

interface WorkflowTimelineProps {
  logs: ApprovalLog[];
}

const actionIcons: Record<string, React.ReactNode> = {
  APPROVE: <CheckCircle2 className="w-5 h-5 text-green-500" />,
  REJECT: <XCircle className="w-5 h-5 text-red-500" />,
  RETURN: <RotateCcw className="w-5 h-5 text-orange-500" />,
  RESUBMIT: <Send className="w-5 h-5 text-blue-500" />,
  START: <PlayCircle className="w-5 h-5 text-blue-500" />,
  COMPLETE: <Flag className="w-5 h-5 text-emerald-500" />,
};

export const WorkflowTimeline: React.FC<WorkflowTimelineProps> = ({ logs }) => {
  if (!logs || logs.length === 0) {
    return <div className="text-gray-500 text-sm italic">No history logs</div>;
  }

  return (
    <div className="flow-root">
      <ul role="list" className="-mb-8">
        {logs.map((log, idx) => (
          <li key={log.id}>
            <div className="relative pb-8">
              {idx !== logs.length - 1 ? (
                <span
                  className="absolute left-4 top-4 -ml-px h-full w-0.5 bg-gray-200 dark:bg-gray-700"
                  aria-hidden="true"
                />
              ) : null}
              <div className="relative flex space-x-3">
                <div>
                  <span className="h-8 w-8 rounded-full bg-white dark:bg-gray-800 flex items-center justify-center ring-8 ring-white dark:ring-gray-900">
                    {actionIcons[log.action] || <CheckCircle2 className="w-5 h-5 text-gray-400" />}
                  </span>
                </div>
                <div className="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
                  <div>
                    <p className="text-sm text-gray-900 dark:text-gray-100 font-medium">
                      {log.user_display}{' '}
                      <span className="font-normal text-gray-500">
                        {log.action === 'APPROVE' && 'approved the request'}
                        {log.action === 'REJECT' && 'rejected the request'}
                        {log.action === 'RETURN' && 'returned for revision'}
                        {log.action === 'RESUBMIT' && 'resubmitted the request'}
                        {log.action === 'COMPLETE' && 'completed the request'}
                      </span>
                    </p>
                    {log.comment && (
                      <div className="mt-2 text-sm text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-800/50 p-2 rounded border border-gray-100 dark:border-gray-700">
                        &quot;{log.comment}&quot;
                      </div>
                    )}
                  </div>
                  <div className="whitespace-nowrap text-right text-xs text-gray-500">
                    <time dateTime={log.created_at}>
                      {format(new Date(log.created_at), 'd MMM yy HH:mm', { locale: enUS })}
                    </time>
                  </div>
                </div>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};
