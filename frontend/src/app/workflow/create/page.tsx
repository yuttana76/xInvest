'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useWorkflowConfigs, useWorkflowMutation } from '@/hooks/useWorkflow';
import { FileUpload } from '@/components/workflow/FileUpload';
import { Button } from '@/components/Button';
import { Input } from '@/components/Input';
import { ChevronLeft, Info } from 'lucide-react';
import Link from 'next/link';

export default function CreateRequestPage() {
  const router = useRouter();
  const { data: configs, isLoading: isLoadingConfigs } = useWorkflowConfigs();
  const { createMutation } = useWorkflowMutation();

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [workflowId, setWorkflowId] = useState('');
  const [files, setFiles] = useState<File[]>([]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title || !workflowId) return;

    const formData = new FormData();
    formData.append('title', title);
    formData.append('description', description);
    formData.append('workflow', workflowId);
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
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Request Type <span className="text-red-500">*</span>
            </label>
            <select
              value={workflowId}
              onChange={(e) => setWorkflowId(e.target.value)}
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
