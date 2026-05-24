import { useRef, useEffect, useState } from 'react';
import MessageBubble from './MessageBubble';
import ChatInput from './ChatInput';
import CitationCard from './CitationCard';

export default function ChatWindow({
  messages,
  isStreaming,
  onSendMessage,
  onFeedback,
  currentSession,
  onCreateSession,
}) {
  const messagesEndRef = useRef(null);
  const [selectedCitations, setSelectedCitations] = useState(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (query) => {
    if (!currentSession) {
      await onCreateSession();
    }
    onSendMessage(query);
  };

  if (!currentSession) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-center p-8">
        <div className="max-w-md space-y-4">
          <h2 className="text-2xl font-display font-bold text-[var(--text-primary)]">
            Welcome to AI Knowledge Base
          </h2>
          <p className="text-[var(--text-secondary)]">
            Upload documents and ask questions. Answers are grounded in your uploaded content
            with source citations and confidence scores.
          </p>
          <button
            onClick={onCreateSession}
            className="px-6 py-2.5 bg-accent hover:bg-accent-hover text-white rounded-lg font-medium transition-colors"
          >
            Start a conversation
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex">
      <div className="flex-1 flex flex-col">
        <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-[var(--text-secondary)] mt-20">
              <p className="text-lg">Ask a question about your documents</p>
              <p className="text-sm mt-1">
                Answers include source citations and confidence scores
              </p>
            </div>
          )}

          {messages.map((msg, i) => (
            <MessageBubble
              key={msg.id || i}
              message={msg}
              onFeedback={onFeedback}
              onShowCitations={setSelectedCitations}
              isStreaming={isStreaming && i === messages.length - 1 && msg.role === 'assistant'}
            />
          ))}
          <div ref={messagesEndRef} />
        </div>

        <ChatInput onSend={handleSend} disabled={isStreaming} />
      </div>

      {selectedCitations && (
        <div className="w-80 border-l border-[var(--border)] bg-white overflow-y-auto p-4 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="font-display font-semibold text-sm">Sources</h3>
            <button
              onClick={() => setSelectedCitations(null)}
              className="text-[var(--text-secondary)] hover:text-[var(--text-primary)] text-sm"
            >
              Close
            </button>
          </div>
          {selectedCitations.map((citation, i) => (
            <CitationCard key={i} citation={citation} />
          ))}
        </div>
      )}
    </div>
  );
}
