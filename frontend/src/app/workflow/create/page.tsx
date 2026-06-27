'use client';

import React, { useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { useWorkflowConfigs, useWorkflowMutation } from '@/hooks/useWorkflow';
import { FileUpload } from '@/components/workflow/FileUpload';
import { Button } from '@/components/Button';
import { Input } from '@/components/Input';
import { ChevronLeft, Info, AlertTriangle, CheckSquare, Square } from 'lucide-react';
import Link from 'next/link';

const PRIORITY_OPTIONS = [
  { value: 1, label: 'High', color: 'text-red-600 dark:text-red-400', bg: 'bg-red-50 dark:bg-red-950/30 border-red-200 dark:border-red-800' },
  { value: 2, label: 'Medium', color: 'text-amber-600 dark:text-amber-400', bg: 'bg-amber-50 dark:bg-amber-950/30 border-amber-200 dark:border-amber-800' },
  { value: 3, label: 'Low', color: 'text-green-600 dark:text-green-400', bg: 'bg-green-50 dark:bg-green-950/30 border-green-200 dark:border-green-800' },
];

export default function CreateRequestPage() {
  const router = useRouter();
  const { data: configs, isLoading: isLoadingConfigs } = useWorkflowConfigs();
  const { createMutation } = useWorkflowMutation();

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [workflowId, setWorkflowId] = useState('');
  const [files, setFiles] = useState<File[]>([]);

  // IT Request fields
  const [selectedSubjects, setSelectedSubjects] = useState<number[]>([]);
  const [priorify, setPriorify] = useState<number>(2); // default Medium
  const [expectDate, setExpectDate] = useState('');
  const [auditFlag, setAuditFlag] = useState(false);

  // Subjects come from the selected workflow config — no extra API call
  const selectedConfig = useMemo(
    () => configs?.find((c) => String(c.id) === workflowId),
    [configs, workflowId]
  );
  const availableSubjects = selectedConfig?.subjects ?? [];

  const handleWorkflowChange = (id: string) => {
    setWorkflowId(id);
    setSelectedSubjects([]); // reset subjects when workflow changes
  };

  const toggleSubject = (id: number) => {
    setSelectedSubjects((prev) =>
      prev.includes(id) ? prev.filter((s) => s !== id) : [...prev, id]
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title || !workflowId) return;

    const formData = new FormData();
    formData.append('title', title);
    formData.append('description', description);
    formData.append('workflow', workflowId);
    formData.append('priorify', String(priorify));
    if (expectDate) formData.append('expectDate', expectDate);
    formData.append('auditFlag', String(auditFlag));
    selectedSubjects.forEach((id) => formData.append('reqSubject', String(id)));
    files.forEach((file) => formData.append('uploaded_files', file));

    createMutation.mutate(formData, {
      onSuccess: () => {
        router.push('/workflow/my-requests');
      },
      onError: (err) => {
        console.error('Failed to create request:', err);
        alert('Error creating request. Please try again.');
      },
    });
  };

  const selectedPriority = PRIORITY_OPTIONS.find((p) => p.value === priorify);

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="flex items-center space-x-2">
        <Link href="/workflow/my-requests">
          <Button variant="ghost" size="icon" className="rounded-full">
            <ChevronLeft className="w-5 h-5" />
          </Button>
        </Link>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Create New Request</h1>
      </div>

      <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 p-6 md:p-8 shadow-sm">
        <form onSubmit={handleSubmit} className="space-y-6">

          {/* Request Type */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Request Type <span className="text-red-500">*</span>
            </label>
            <select
              value={workflowId}
              onChange={(e) => handleWorkflowChange(e.target.value)}
              required
              className="flex h-11 w-full rounded-xl border border-gray-200 dark:border-white/10 bg-white dark:bg-white/5 px-4 py-2 text-sm focus:ring-2 focus:ring-primary/20 outline-none transition-all"
            >
              <option value="">Select Workflow Type</option>
              {configs?.map((config) => (
                <option key={config.id} value={config.id}>
                  {config.name}
                </option>
              ))}
            </select>
          </div>

          {/* Title */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Title <span className="text-red-500">*</span>
            </label>
            <Input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Enter a short title"
              required
            />
          </div>

          {/* Subject (multi-choice — scoped to selected workflow) */}
          {workflowId && (
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Subject{' '}
                <span className="text-xs font-normal text-gray-500">(select all that apply)</span>
              </label>
              {availableSubjects.length > 0 ? (
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
              ) : (
                <p className="text-sm text-gray-400 italic px-1">
                  No subjects configured for this workflow. Ask your admin to add subjects in the admin panel.
                </p>
              )}
            </div>
          )}

          {/* Priority */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Priority</label>
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
            {selectedPriority && (
              <p className={`text-xs ${selectedPriority.color}`}>
                Selected: <strong>{selectedPriority.label}</strong> priority
              </p>
            )}
          </div>

          {/* Expected Completion Date */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Expected Completion Date{' '}
              <span className="text-xs font-normal text-gray-500">(optional)</span>
            </label>
            <input
              type="date"
              value={expectDate}
              onChange={(e) => setExpectDate(e.target.value)}
              min={new Date().toISOString().split('T')[0]}
              className="flex h-11 w-full rounded-xl border border-gray-200 dark:border-white/10 bg-white dark:bg-white/5 px-4 py-2 text-sm focus:ring-2 focus:ring-primary/20 outline-none transition-all"
            />
          </div>

          {/* Description */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Additional details (optional)"
              rows={4}
              className="flex w-full rounded-xl border border-gray-200 dark:border-white/10 bg-white dark:bg-white/5 px-4 py-2 text-sm focus:ring-2 focus:ring-primary/20 outline-none transition-all"
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

          {/* Attachments */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Attachments</label>
            <FileUpload files={files} onChange={setFiles} />
            <p className="flex items-center text-xs text-gray-500 gap-1.5 mt-2">
              <Info className="w-3 h-3" />
              Attach relevant proof or documents
            </p>
          </div>

          <div className="pt-4 flex gap-3">
            <Button
              type="submit"
              className="flex-1"
              disabled={createMutation.isPending || isLoadingConfigs}
            >
              {createMutation.isPending ? 'Submitting...' : 'Submit Request'}
            </Button>
            <Link href="/workflow/my-requests" className="flex-1">
              <Button type="button" variant="outline" className="w-full">
                Cancel
              </Button>
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}
