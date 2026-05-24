import { MessageSquare, FileText, BarChart3, Plus } from 'lucide-react';
import StatusIndicator from './StatusIndicator';

const navItems = [
  { id: 'chat', label: 'Chat', icon: MessageSquare },
  { id: 'documents', label: 'Documents', icon: FileText },
  { id: 'analytics', label: 'Analytics', icon: BarChart3 },
];

export default function Sidebar({
  activeView,
  onNavigate,
  health,
  sessions,
  currentSession,
  onSelectSession,
  onNewSession,
}) {
  return (
    <aside className="w-60 bg-sidebar text-[var(--text-sidebar)] flex flex-col h-full">
      <div className="p-4 border-b border-white/10">
        <h1 className="text-lg font-display font-bold tracking-tight">AI Knowledge Base</h1>
      </div>

      <nav className="p-2 space-y-1">
        {navItems.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => onNavigate(id)}
            className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
              activeView === id
                ? 'bg-white/10 text-white'
                : 'text-gray-400 hover:bg-white/5 hover:text-gray-200'
            }`}
          >
            <Icon size={18} />
            {label}
          </button>
        ))}
      </nav>

      {activeView === 'chat' && (
        <div className="flex-1 flex flex-col overflow-hidden mt-2 border-t border-white/10">
          <div className="p-2">
            <button
              onClick={onNewSession}
              className="w-full flex items-center gap-2 px-3 py-2 text-sm rounded-lg bg-accent hover:bg-accent-hover text-white transition-colors"
            >
              <Plus size={16} />
              New Chat
            </button>
          </div>
          <div className="flex-1 overflow-y-auto px-2 space-y-0.5">
            {sessions.map((s) => (
              <button
                key={s.id}
                onClick={() => onSelectSession(s)}
                className={`w-full text-left px-3 py-2 text-sm rounded-lg truncate transition-colors ${
                  currentSession?.id === s.id
                    ? 'bg-white/10 text-white'
                    : 'text-gray-400 hover:bg-white/5'
                }`}
              >
                {s.title || 'New conversation'}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="p-3 border-t border-white/10 space-y-1.5">
        <StatusIndicator label="Backend" status={health.postgres} />
        <StatusIndicator label="LLM (Groq)" status={health.llm} />
        <StatusIndicator label="Vector DB" status={health.qdrant} />
      </div>
    </aside>
  );
}
