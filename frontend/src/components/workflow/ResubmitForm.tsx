import React, { useState } from 'react';
import { WorkflowRequest } from '@/lib/api/workflow';
import { useWorkflowMutation, useWorkflowConfigs } from '@/hooks/useWorkflow';
import { FileUpload } from '@/components/workflow/FileUpload';
import { Button } from '@/components/Button';
import { Input } from '@/components/Input';
import { Send, AlertTriangle, CheckSquare, Square } from 'lucide-react';

interface ResubmitFormProps {
  request: WorkflowRequest;
  onSuccess?: () => void;
}

const PRIORITY_OPTIONS = [
  { value: 1, label: 'High', color: 'text-red-600 dark:text-red-400', bg: 'bg-red-50 dark:bg-red-950/30 border-red-200 dark:border-red-800' },
  { value: 2, label: 'Medium', color: 'text-amber-600 dark:text-amber-400', bg: 'bg-amber-50 dark:bg-amber-950/30 border-amber-200 dark:border-amber-800' },
  { value: 3, label: 'Low', color: 'text-green-600 dark:text-green-400', bg: 'bg-green-50 dark:bg-green-950/30 border-green-200 dark:border-green-800' },
];

export const ResubmitForm: React.FC<ResubmitFormProps> = ({ request, onSuccess }) => {
  const [title, setTitle] = useState(request.title);
  const [description, setDescription] = useState(request.description);
  const [comment, setComment] = useState('');
  const [files, setFiles] = useState<File[]>([]);

  // IT Request fields — pre-populated from the existing request
  const [selectedSubjects, setSelectedSubjects] = useState<number[]>(request.reqSubject ?? []);
  const [priorify, setPriorify] = useState<number>(request.priorify ?? 2);
  const [expectDate, setExpectDate] = useState<string>(request.expectDate ?? '');
  const [auditFlag, setAuditFlag] = useState<boolean>(request.auditFlag ?? false);

  const { resubmitMutation } = useWorkflowMutation();

  // Read subjects from the workflow config (already fetched) — scoped to this request's workflow
  const { data: configs } = useWorkflowConfigs();
  const workflowConfig = configs?.find((c) => c.id === request.workflow);
  const availableSubjects = workflowConfig?.subjects ?? [];

  const toggleSubject = (id: number) => {
    setSelectedSubjects((prev) =>
      prev.includes(id) ? prev.filter((s) => s !== id) : [...prev, id]
    );
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!comment) {
      alert('Please provide internal revision notes.');
      return;
    }

    const formData = new FormData();
    formData.append('title', title);
    formData.append('description', description);
    formData.append('comment', comment);
    formData.append('priorify', String(priorify));
    if (expectDate) formData.append('expectDate', expectDate);
    formData.append('auditFlag', String(auditFlag));
    selectedSubjects.forEach((id) => formData.append('reqSubject', String(id)));
    files.forEach((file) => formData.append('uploaded_files', file));

    resubmitMutation.mutate({ id: request.id, formData }, {
      onSuccess: () => {
        setFiles([]);
        setComment('');
        onSuccess?.();
      }
    });
  };

  const lastReturnLog = [...(request.logs || [])].reverse().find(l => l.action === 'RETURN');

  return (
    <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6 shadow-sm mt-6">
      <h3 className="text-lg font-bold mb-4 text-orange-600">Revise and Resubmit</h3>

      {lastReturnLog && (
        <div className="mb-6 p-4 bg-orange-50 dark:bg-orange-950/20 border border-orange-200 dark:border-orange-900/50 rounded-xl">
          <p className="text-xs font-bold text-orange-800 dark:text-orange-400 uppercase tracking-wider mb-2">
            Reason for return from {lastReturnLog.user_display || lastReturnLog.approver_name}:
          </p>
          <p className="text-sm text-orange-700 dark:text-orange-300 italic">
            &quot;{lastReturnLog.comment}&quot;
          </p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Title */}
        <div>
          <label className="block text-sm font-medium mb-1">Title</label>
          <Input value={title} onChange={(e) => setTitle(e.target.value)} required />
        </div>

        {/* Subject (multi-choice — scoped to the request's workflow) */}
        {availableSubjects.length > 0 && (
          <div>
            <label className="block text-sm font-medium mb-1">
              Subject{' '}
              <span className="text-xs font-normal text-gray-500">(select all that apply)</span>
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {availableSubjects.map((subject) => {
                const isSelected = selectedSubjects.includes(subject.id);
                return (
                  <button
                    key={subject.id}
                    type="button"
                    onClick={() => toggleSubject(subject.id)}
                    className={`flex items-center gap-2.5 px-4 py-2.5 rounded-xl border text-sm text-left transition-all ${
                      isSelected
                        ? 'bg-blue-50 dark:bg-blue-950/30 border-blue-400 dark:border-blue-600 text-blue-700 dark:text-blue-300 font-medium'
                        : 'border-gray-200 dark:border-white/10 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-white/5'
                    }`}
                  >
                    {isSelected
                      ? <CheckSquare className="w-4 h-4 flex-shrink-0" />
                      : <Square className="w-4 h-4 flex-shrink-0" />
                    }
                    {subject.name}
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* Priority */}
        <div>
          <label className="block text-sm font-medium mb-1">Priority</label>
          <div className="flex gap-2">
            {PRIORITY_OPTIONS.map((opt) => (
              <button
                key={opt.value}
                type="button"
                onClick={() => setPriorify(opt.value)}
                className={`flex-1 py-2 rounded-xl border text-sm font-medium transition-all ${
                  priorify === opt.value
                    ? `${opt.bg} ${opt.color} border-current`
                    : 'border-gray-200 dark:border-white/10 text-gray-500 hover:bg-gray-50 dark:hover:bg-white/5'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        {/* Expected Completion Date */}
        <div>
          <label className="block text-sm font-medium mb-1">
            Expected Completion Date{' '}
            <span className="text-xs font-normal text-gray-500">(optional)</span>
          </label>
          <input
            type="date"
            value={expectDate}
            onChange={(e) => setExpectDate(e.target.value)}
            className="flex h-11 w-full rounded-xl border border-gray-200 dark:border-white/10 bg-white dark:bg-white/5 px-4 py-2 text-sm focus:ring-2 focus:ring-primary/20 outline-none transition-all"
          />
        </div>

        {/* Audit Flag */}
        <div className="flex items-start gap-3 p-4 rounded-xl border border-gray-200 dark:border-white/10 bg-gray-50 dark:bg-white/5">
          <button
            type="button"
            onClick={() => setAuditFlag((v) => !v)}
            className={`mt-0.5 flex-shrink-0 transition-colors ${
              auditFlag ? 'text-amber-600 dark:text-amber-400' : 'text-gray-400'
            }`}
          >
            {auditFlag ? <CheckSquare className="w-5 h-5" /> : <Square className="w-5 h-5" />}
          </button>
          <div>
            <div className="flex items-center gap-1.5">
              <AlertTriangle className={`w-4 h-4 ${auditFlag ? 'text-amber-500' : 'text-gray-400'}`} />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Mark as Audit Case</span>
            </div>
            <p className="text-xs text-gray-500 mt-0.5">
              Check this if the request is critical for IT audit records
            </p>
          </div>
        </div>

        {/* Additional Details */}
        <div>
          <label className="block text-sm font-medium mb-1">Additional Details</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full rounded-xl border border-gray-200 dark:border-white/10 bg-white dark:bg-white/5 px-4 py-2 text-sm focus:ring-2 focus:ring-primary/20 outline-none transition-all"
            rows={3}
          />
        </div>

        {/* Revision Notes */}
        <div>
          <label className="block text-sm font-medium mb-1 text-orange-600">
            Revision Notes <span className="text-red-500">*</span>
          </label>
          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Explain what you have revised"
            className="w-full rounded-xl border border-gray-200 dark:border-white/10 bg-white dark:bg-white/5 px-4 py-2 text-sm focus:ring-2 focus:ring-primary/20 outline-none transition-all"
            rows={3}
            required
          />
        </div>

        {/* File Upload */}
        <div>
          <label className="block text-sm font-medium mb-1">Attach more files (optional)</label>
          <FileUpload files={files} onChange={setFiles} />
        </div>

        <Button
          type="submit"
          className="w-full bg-orange-600 hover:bg-orange-700"
          disabled={resubmitMutation.isPending}
        >
          <Send className="w-4 h-4 mr-2" />
          {resubmitMutation.isPending ? 'Resubmitting...' : 'Resubmit Request'}
        </Button>
      </form>
    </div>
  );
};
