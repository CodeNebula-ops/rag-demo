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
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const chat = useChat();
  const docs = useDocuments();
  const health = useHealth();

  useEffect(() => {
    chat.loadSessions();
    docs.loadDocuments();
  }, []);

  const handleNavigate = (view) => {
    setActiveView(view);
    setSidebarOpen(false);
  };

  const handleSelectSession = (session) => {
    chat.selectSession(session);
    setSidebarOpen(false);
  };

  return (
    <div className="flex h-screen bg-[var(--bg-primary)]">
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/40 z-20 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <Sidebar
        activeView={activeView}
        onNavigate={handleNavigate}
        health={health}
        sessions={chat.sessions}
        currentSession={chat.currentSession}
        onSelectSession={handleSelectSession}
        onNewSession={chat.createSession}
        onDeleteSession={chat.deleteSession}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      <div className="flex-1 flex flex-col overflow-hidden min-w-0">
        <Header
          activeView={activeView}
          health={health}
          onMenuToggle={() => setSidebarOpen(!sidebarOpen)}
        />

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
            <div className="h-full overflow-y-auto p-4 md:p-6 space-y-6">
              <DocumentUpload
                onUpload={docs.uploadDocument}
                uploading={docs.uploading}
                progress={docs.uploadProgress}
              />
              <DocumentList
                documents={docs.documents}
                onDelete={docs.deleteDocument}
                onRefresh={docs.loadDocuments}
                onReprocess={docs.reprocessDocument}
              />
            </div>
          )}

          {activeView === 'analytics' && (
            <div className="h-full overflow-y-auto p-4 md:p-6 space-y-6">
              <UsageDashboard />
              <ContentGapsList />
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
