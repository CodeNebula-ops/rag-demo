import { useState, useEffect } from 'react';
import Sidebar from './components/layout/Sidebar';
import Header from './components/layout/Header';
import ChatWindow from './components/chat/ChatWindow';
import DocumentUpload from './components/documents/DocumentUpload';
import DocumentList from './components/documents/DocumentList';
import UsageDashboard from './components/analytics/UsageDashboard';
import ContentGapsList from './components/analytics/ContentGapsList';
import { useChat } from './hooks/useChat';
import { useDocuments } from './hooks/useDocuments';
import { useHealth } from './hooks/useHealth';

export default function App() {
  const [activeView, setActiveView] = useState('chat');
  const chat = useChat();
  const docs = useDocuments();
  const health = useHealth();

  useEffect(() => {
    chat.loadSessions();
    docs.loadDocuments();
  }, []);

  return (
    <div className="flex h-screen bg-[var(--bg-primary)]">
      <Sidebar
        activeView={activeView}
        onNavigate={setActiveView}
        health={health}
        sessions={chat.sessions}
        currentSession={chat.currentSession}
        onSelectSession={chat.selectSession}
        onNewSession={chat.createSession}
      />

      <div className="flex-1 flex flex-col overflow-hidden">
        <Header activeView={activeView} health={health} />

        <main className="flex-1 overflow-hidden">
          {activeView === 'chat' && (
            <ChatWindow
              messages={chat.messages}
              isStreaming={chat.isStreaming}
              onSendMessage={chat.sendMessage}
              onFeedback={chat.submitFeedback}
              currentSession={chat.currentSession}
              onCreateSession={chat.createSession}
            />
          )}

          {activeView === 'documents' && (
            <div className="h-full overflow-y-auto p-6 space-y-6">
              <DocumentUpload
                onUpload={docs.uploadDocument}
                uploading={docs.uploading}
                progress={docs.uploadProgress}
              />
              <DocumentList
                documents={docs.documents}
                onDelete={docs.deleteDocument}
                onRefresh={docs.loadDocuments}
              />
            </div>
          )}

          {activeView === 'analytics' && (
            <div className="h-full overflow-y-auto p-6 space-y-6">
              <UsageDashboard />
              <ContentGapsList />
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
