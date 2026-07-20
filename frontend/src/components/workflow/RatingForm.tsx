'use client';

import React, { useState } from 'react';
import { Star } from 'lucide-react';
import { Button } from '@/components/Button';
import { useWorkflowMutation } from '@/hooks/useWorkflow';
import { WorkflowRequest } from '@/lib/api/workflow';

interface RatingFormProps {
  request: WorkflowRequest;
  isCreator?: boolean;
}

export function RatingForm({ request, isCreator }: RatingFormProps) {
  const [rating, setRating] = useState<number>(0);
  const [hover, setHover] = useState<number>(0);
  const [comment, setComment] = useState<string>('');
  const { rateMutation } = useWorkflowMutation();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (rating === 0) {
      alert("Please select a rating");
      return;
    }

    try {
      await rateMutation.mutateAsync({
        id: request.id,
        rating,
        comment,
      });
      alert("Satisfaction rating saved successfully");
    } catch (err) {
      console.error(err);
      alert("Failed to save rating. Please try again.");
    }
  };

  if (request.rating !== null && request.rating !== undefined) {
    // Already rated - show results
    return (
      <div className="bg-green-50 dark:bg-green-900/10 p-6 rounded-2xl border border-green-100 dark:border-green-800/30">
        <h3 className="text-lg font-bold text-green-800 dark:text-green-400 mb-2">Thank you for your feedback!</h3>
        <div className="flex items-center space-x-1 mb-3">
          {[1, 2, 3, 4, 5].map((star) => (
            <Star
              key={star}
              className={`w-5 h-5 ${star <= request.rating! ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'}`}
            />
          ))}
        </div>
        {request.rating_comment && (
          <p className="text-sm text-gray-600 dark:text-gray-400 italic">&quot;{request.rating_comment}&quot;</p>
        )}
      </div>
    );
  }

  if (!isCreator) {
    // Not creator and not rated - show status
    return (
      <div className="bg-gray-50 dark:bg-gray-900/50 p-6 rounded-2xl border border-dashed border-gray-200 dark:border-gray-800 text-center">
        <Star className="w-8 h-8 mx-auto mb-2 text-gray-300" />
        <p className="text-sm text-gray-500 italic">Waiting for creator to rate satisfaction...</p>
      </div>
    );
  }

  // Creator hasn't rated yet - show form
  return (
    <div className="bg-primary/5 p-6 rounded-2xl border border-primary/10 shadow-sm">
      <h3 className="text-lg font-bold mb-1">Rate Satisfaction</h3>
      <p className="text-sm text-gray-500 mb-6">Your rating helps us improve our service in the future.</p>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="flex items-center space-x-2 justify-center py-2">
          {[1, 2, 3, 4, 5].map((star) => (
            <button
              key={star}
              type="button"
              className="focus:outline-none transition-transform active:scale-95"
              onClick={() => setRating(star)}
              onMouseEnter={() => setHover(star)}
              onMouseLeave={() => setHover(0)}
            >
              <Star
                className={`w-10 h-10 ${
                  star <= (hover || rating)
                    ? 'fill-yellow-400 text-yellow-400'
                    : 'text-gray-300 dark:text-gray-700'
                } transition-colors`}
              />
            </button>
          ))}
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium">Additional Feedback (Optional)</label>
          <textarea
            className="w-full p-3 rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 focus:ring-2 focus:ring-primary/20 outline-none transition-all resize-none h-24 text-sm"
            placeholder="Share your thoughts or suggestions..."
            value={comment}
            onChange={(e) => setComment(e.target.value)}
          />
        </div>

        <Button 
          type="submit" 
          className="w-full py-6 text-base font-bold shadow-lg shadow-primary/20"
          disabled={rateMutation.isPending || rating === 0}
        >
          {rateMutation.isPending ? 'Saving...' : 'Submit Satisfaction Rating'}
        </Button>
      </form>
    </div>
  );
}
