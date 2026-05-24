import { ThumbsUp, ThumbsDown } from 'lucide-react';

export default function FeedbackButtons({ messageId, feedback, onFeedback }) {
  if (messageId === 'streaming') return null;

  return (
    <div className="flex items-center gap-1 ml-auto">
      <button
        onClick={() => onFeedback(messageId, 'up')}
        className={`p-1 rounded transition-colors ${
          feedback === 'up'
            ? 'text-[var(--success)]'
            : 'text-gray-300 hover:text-gray-500'
        }`}
        title="Helpful"
      >
        <ThumbsUp size={14} />
      </button>
      <button
        onClick={() => onFeedback(messageId, 'down')}
        className={`p-1 rounded transition-colors ${
          feedback === 'down'
            ? 'text-[var(--danger)]'
            : 'text-gray-300 hover:text-gray-500'
        }`}
        title="Not helpful"
      >
        <ThumbsDown size={14} />
      </button>
    </div>
  );
}
