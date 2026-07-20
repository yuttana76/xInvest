import React, { useState } from 'react';
import { Button } from '@/components/Button';
import { useWorkflowMutation } from '@/hooks/useWorkflow';
import { CheckCircle2, XCircle, RotateCcw, Star } from 'lucide-react';
import { FileUpload } from './FileUpload';

interface ActionPanelProps {
  requestId: number;
  status?: string;
}

export const ActionPanel: React.FC<ActionPanelProps> = ({ requestId, status }) => {
  const [comment, setComment] = useState('');
  const [rating, setRating] = useState(0);
  const [ratingHover, setRatingHover] = useState(0);
  const [files, setFiles] = useState<File[]>([]);
  const { approveMutation, rejectMutation, returnMutation, completeMutation, rateMutation } = useWorkflowMutation();

  const handleAction = (mutation: any) => {
    if ((mutation === rejectMutation || mutation === returnMutation) && !comment) {
      alert('Please provide a comment for rejection or return.');
      return;
    }
    
    if (mutation === approveMutation) {
      mutation.mutate({ id: requestId, comment, files }, {
        onSuccess: () => {
          setComment('');
          setFiles([]);
        }
      });
    } else {
      mutation.mutate({ id: requestId, comment }, {
        onSuccess: () => {
          setComment('');
        }
      });
    }
  };

  const handleCompleteWithRating = async () => {
    if (rating === 0) {
      alert('Please provide a satisfaction rating before completing.');
      return;
    }

    try {
      // Perform both actions in one call to the updated 'complete' API
      await completeMutation.mutateAsync({
        id: requestId,
        comment: comment,
        rating: rating,
        rating_comment: comment, // Using the same comment for both
      });
      
      alert('Request completed and feedback saved.');
    } catch (err) {
      console.error(err);
      alert('Failed to complete request. Please try again.');
    }
  };

  const isPending = approveMutation.isPending || rejectMutation.isPending || returnMutation.isPending || completeMutation.isPending || rateMutation.isPending;

  return (
    <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6 shadow-sm">
      <h3 className="text-lg font-bold mb-4">
        {status === 'APPROVED' ? 'Confirm Completion & Feedback' : 'Action'}
      </h3>
      
      <div className="space-y-4">
        {status === 'APPROVED' && (
          <div className="bg-primary/5 p-4 rounded-xl border border-primary/10 mb-2">
            <label className="block text-sm font-semibold text-center mb-3">
              How satisfied are you with the outcome?
            </label>
            <div className="flex items-center space-x-2 justify-center py-1">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  type="button"
                  className="focus:outline-none transition-transform active:scale-95"
                  onClick={() => setRating(star)}
                  onMouseEnter={() => setRatingHover(star)}
                  onMouseLeave={() => setRatingHover(0)}
                >
                  <Star
                    className={`w-8 h-8 ${
                      star <= (ratingHover || rating)
                        ? 'fill-yellow-400 text-yellow-400'
                        : 'text-gray-300 dark:text-gray-700'
                    } transition-colors`}
                  />
                </button>
              ))}
            </div>
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            {status === 'APPROVED' ? 'Additional Feedback (Optional)' : 'Comment / Remarks'}
          </label>
          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder={status === 'APPROVED' ? 'Enter completion notes (optional)' : 'Enter rationale (required for rejection/return)'}
            className="w-full rounded-xl border border-gray-200 dark:border-white/10 bg-white dark:bg-white/5 px-4 py-2 text-sm focus:ring-2 focus:ring-primary/20 outline-none transition-all"
            rows={3}
          />
        </div>

        {status !== 'APPROVED' && (
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Attach Files (Optional)
            </label>
            <FileUpload files={files} onChange={setFiles} />
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {status === 'APPROVED' ? (
            <Button
              onClick={handleCompleteWithRating}
              disabled={isPending || (status === 'APPROVED' && rating === 0)}
              className="sm:col-span-3 bg-emerald-600 hover:bg-emerald-700 shadow-emerald-500/20 py-6 text-base"
            >
              <CheckCircle2 className="w-5 h-5 mr-2" />
              Confirm Completion & Submit Rating
            </Button>
          ) : (
            <>
              <Button
                onClick={() => handleAction(approveMutation)}
                disabled={isPending}
                className="bg-green-600 hover:bg-green-700 shadow-green-500/20"
              >
                <CheckCircle2 className="w-4 h-4 mr-2" />
                Approve
              </Button>
              
              <Button
                variant="outline"
                onClick={() => handleAction(returnMutation)}
                disabled={isPending}
                className="text-orange-600 border-orange-200 hover:bg-orange-50 dark:hover:bg-orange-900/10"
              >
                <RotateCcw className="w-4 h-4 mr-2" />
                Return for Revision
              </Button>

              <Button
                variant="outline"
                onClick={() => handleAction(rejectMutation)}
                disabled={isPending}
                className="text-red-600 border-red-200 hover:bg-red-50 dark:hover:bg-red-900/10"
              >
                <XCircle className="w-4 h-4 mr-2" />
                Reject
              </Button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};
