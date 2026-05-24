import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import ConfidenceBadge from './ConfidenceBadge';
import FeedbackButtons from './FeedbackButtons';
import { formatLatency } from '../../utils/formatters';

export default function MessageBubble({ message, onFeedback, onShowCitations, isStreaming }) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[88%] md:max-w-[75%] rounded-2xl px-4 py-3 ${
          isUser
            ? 'bg-sidebar text-white'
            : 'bg-white text-[var(--text-primary)] border border-[var(--border)]'
        }`}
      >
        <div className="prose prose-sm max-w-none">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
        </div>

        {isStreaming && !message.content && (
          <div className="flex items-center gap-1.5 py-2">
            <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
            <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
            <span className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
        )}

        {!isUser && !isStreaming && message.content && (
          <div className="mt-2.5 pt-2 border-t border-gray-100 flex items-center gap-2 flex-wrap">
            {message.confidence_score != null && (
              <ConfidenceBadge
                score={message.confidence_score}
                level={message.confidence_level}
              />
            )}

            {message.citations && message.citations.length > 0 && (
              <button
                onClick={() => onShowCitations(message.citations)}
                className="text-xs text-sidebar hover:underline font-medium"
              >
                {message.citations.length} source{message.citations.length > 1 ? 's' : ''}
              </button>
            )}

            {message.latency_ms && (
              <span className="text-[11px] text-gray-400">
                {formatLatency(message.latency_ms)}
              </span>
            )}

            <FeedbackButtons
              messageId={message.id}
              feedback={message.feedback}
              onFeedback={onFeedback}
            />
          </div>
        )}
      </div>
    </div>
  );
}
