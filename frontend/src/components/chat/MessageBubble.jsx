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
        className={`max-w-[75%] rounded-2xl px-4 py-3 ${
          isUser
            ? 'bg-[var(--bg-user-msg)] text-[var(--text-primary)]'
            : 'bg-[var(--bg-ai-msg)] text-[var(--text-primary)]'
        }`}
      >
        <div className="prose prose-sm max-w-none">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
        </div>

        {isStreaming && !message.content && (
          <div className="flex items-center gap-1 py-2">
            <span className="w-2 h-2 bg-accent rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
            <span className="w-2 h-2 bg-accent rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
            <span className="w-2 h-2 bg-accent rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
        )}

        {!isUser && !isStreaming && message.content && (
          <div className="mt-3 pt-2 border-t border-black/5 flex items-center gap-3 flex-wrap">
            {message.confidence_score != null && (
              <ConfidenceBadge
                score={message.confidence_score}
                level={message.confidence_level}
              />
            )}

            {message.citations && message.citations.length > 0 && (
              <button
                onClick={() => onShowCitations(message.citations)}
                className="text-xs text-accent hover:text-accent-hover font-medium"
              >
                {message.citations.length} source{message.citations.length > 1 ? 's' : ''}
              </button>
            )}

            {message.latency_ms && (
              <span className="text-xs text-[var(--text-secondary)]">
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
