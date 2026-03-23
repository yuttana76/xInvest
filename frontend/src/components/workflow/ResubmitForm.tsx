import React, { useState } from 'react';
import { WorkflowRequest } from '@/lib/api/workflow';
import { useWorkflowMutation } from '@/hooks/useWorkflow';
import { FileUpload } from '@/components/workflow/FileUpload';
import { Button } from '@/components/Button';
import { Input } from '@/components/Input';
import { Send } from 'lucide-react';

interface ResubmitFormProps {
  request: WorkflowRequest;
  onSuccess?: () => void;
}

export const ResubmitForm: React.FC<ResubmitFormProps> = ({ request, onSuccess }) => {
  const [title, setTitle] = useState(request.title);
  const [description, setDescription] = useState(request.description);
  const [comment, setComment] = useState('');
  const [files, setFiles] = useState<File[]>([]);
  const { resubmitMutation } = useWorkflowMutation();

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

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Title</label>
          <Input value={title} onChange={(e) => setTitle(e.target.value)} required />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Additional Details</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full rounded-xl border border-gray-200 dark:border-white/10 bg-white dark:bg-white/5 px-4 py-2 text-sm focus:ring-2 focus:ring-primary/20 outline-none transition-all"
            rows={3}
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1 text-orange-600">
            Revision Notes <span className="text-red-500">*</span>
          </label>
          <Input 
            value={comment} 
            onChange={(e) => setComment(e.target.value)} 
            placeholder="Explain what you have revised"
            required 
          />
        </div>
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
