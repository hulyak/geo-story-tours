'use client';

import { useState } from 'react';
import { Star, ThumbsUp, ThumbsDown, Send } from 'lucide-react';

interface TourRatingProps {
  tourId: string;
}

export default function TourRating({ tourId }: TourRatingProps) {
  const [rating, setRating] = useState(0);
  const [hoveredRating, setHoveredRating] = useState(0);
  const [feedback, setFeedback] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [helpfulVote, setHelpfulVote] = useState<'up' | 'down' | null>(null);

  const handleSubmit = async () => {
    if (rating === 0) {
      alert('Please select a rating');
      return;
    }

    setSubmitting(true);

    try {
      const response = await fetch('/api/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          tour_id: tourId,
          rating,
          feedback,
          helpful_vote: helpfulVote,
          timestamp: new Date().toISOString(),
        }),
      });

      const data = await response.json();

      if (data.success) {
        setSubmitted(true);
      } else {
        alert('Failed to submit feedback. Please try again.');
      }
    } catch (error) {
      console.error('Error submitting feedback:', error);
      alert('Failed to submit feedback. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-2xl p-8 border-2 border-green-200">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-green-600 rounded-full mb-4">
            <span className="text-3xl">✓</span>
          </div>
          <h3 className="text-2xl font-bold text-gray-900 mb-2">Thank You!</h3>
          <p className="text-gray-600">
            Your feedback helps us improve tours for everyone. We really appreciate it!
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl shadow-lg p-8">
      <h3 className="text-2xl font-bold text-gray-900 mb-2">Rate This Tour</h3>
      <p className="text-gray-600 mb-6">
        Help us improve by sharing your experience
      </p>

      {/* Star Rating */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-3">
          How would you rate this tour?
        </label>
        <div className="flex gap-2">
          {[1, 2, 3, 4, 5].map((star) => (
            <button
              key={star}
              type="button"
              onClick={() => setRating(star)}
              onMouseEnter={() => setHoveredRating(star)}
              onMouseLeave={() => setHoveredRating(0)}
              className="transition-transform hover:scale-110"
            >
              <Star
                className={`h-10 w-10 ${
                  star <= (hoveredRating || rating)
                    ? 'fill-yellow-400 text-yellow-400'
                    : 'text-gray-300'
                }`}
              />
            </button>
          ))}
        </div>
        {rating > 0 && (
          <p className="mt-2 text-sm text-gray-600">
            {rating === 1 && '😞 Poor - Needs improvement'}
            {rating === 2 && '😐 Fair - Could be better'}
            {rating === 3 && '🙂 Good - Met expectations'}
            {rating === 4 && '😊 Very Good - Enjoyed it!'}
            {rating === 5 && '🤩 Excellent - Loved it!'}
          </p>
        )}
      </div>

      {/* Was Tour Helpful */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Was this tour helpful?
        </label>
        <div className="flex gap-3">
          <button
            type="button"
            onClick={() => setHelpfulVote(helpfulVote === 'up' ? null : 'up')}
            className={`flex items-center gap-2 px-6 py-3 rounded-xl font-medium transition-all ${
              helpfulVote === 'up'
                ? 'bg-green-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <ThumbsUp className="h-5 w-5" />
            Yes, helpful
          </button>
          <button
            type="button"
            onClick={() => setHelpfulVote(helpfulVote === 'down' ? null : 'down')}
            className={`flex items-center gap-2 px-6 py-3 rounded-xl font-medium transition-all ${
              helpfulVote === 'down'
                ? 'bg-red-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <ThumbsDown className="h-5 w-5" />
            Not helpful
          </button>
        </div>
      </div>

      {/* Feedback Text */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-3">
          Additional Feedback (Optional)
        </label>
        <textarea
          value={feedback}
          onChange={(e) => setFeedback(e.target.value)}
          placeholder="Tell us what you liked or what could be improved..."
          rows={4}
          className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-600 focus:border-transparent resize-none"
        />
        <p className="mt-2 text-sm text-gray-500">
          {feedback.length}/500 characters
        </p>
      </div>

      {/* Submit Button */}
      <button
        type="button"
        onClick={handleSubmit}
        disabled={submitting || rating === 0}
        className="w-full px-6 py-4 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-xl font-semibold hover:shadow-lg transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center gap-2"
      >
        {submitting ? (
          <>
            <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
            Submitting...
          </>
        ) : (
          <>
            <Send className="h-5 w-5" />
            Submit Feedback
          </>
        )}
      </button>
    </div>
  );
}
