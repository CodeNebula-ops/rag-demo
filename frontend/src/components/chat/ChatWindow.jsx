import { useRef, useEffect, useState } from 'react';
import { X } from 'lucide-react';
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
    let session = currentSession;
    if (!session) {
      session = await onCreateSession();
    }
    onSendMessage(query, session);
  };

  if (!currentSession) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-center p-6">
        <div className="max-w-sm space-y-3">
          <div className="w-12 h-12 rounded-2xl bg-sidebar flex items-center justify-center mx-auto mb-4">
            <span className="text-white font-display font-bold text-lg">R</span>
          </div>
          <h2 className="text-xl font-display font-bold text-[var(--text-primary)]">
            Retrion
          </h2>
          <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
            Upload documents and ask questions. Answers are grounded in your content with citations.
          </p>
          <button
            onClick={onCreateSession}
            className="mt-4 px-5 py-2.5 bg-sidebar hover:bg-[#252547] text-white rounded-lg text-sm font-medium transition-colors"
          >
            Start a conversation
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex relative">
      <div className="flex-1 flex flex-col min-w-0">
        <div className="flex-1 overflow-y-auto px-3 md:px-4 py-6 space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-[var(--text-secondary)] mt-16">
              <p className="text-base">Ask anything about your documents</p>
              <p className="text-xs mt-1 text-gray-400">
                Responses include sources and confidence scores
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
        <>
          <div
            className="fixed inset-0 bg-black/30 z-10 lg:hidden"
            onClick={() => setSelectedCitations(null)}
          />
          <div className="fixed right-0 top-0 bottom-0 w-[85%] max-w-sm lg:static lg:w-80 border-l border-[var(--border)] bg-white overflow-y-auto p-4 space-y-3 z-20 shadow-xl lg:shadow-none">
            <div className="flex items-center justify-between mb-1">
              <h3 className="font-display font-semibold text-sm">Sources</h3>
              <button
                onClick={() => setSelectedCitations(null)}
                className="p-1 text-[var(--text-secondary)] hover:text-[var(--text-primary)] rounded"
              >
                <X size={16} />
              </button>
            </div>
            {selectedCitations.map((citation, i) => (
              <CitationCard key={i} citation={citation} />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
