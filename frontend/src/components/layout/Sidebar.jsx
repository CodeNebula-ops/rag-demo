import { MessageSquare, FileText, BarChart3, Plus, X, Trash2 } from 'lucide-react';
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
  onDeleteSession,
  isOpen,
  onClose,
}) {
  return (
    <aside
      className={`fixed lg:static inset-y-0 left-0 z-30 w-64 bg-sidebar text-[var(--text-sidebar)] flex flex-col h-full transition-transform duration-200 ease-in-out ${
        isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
      }`}
    >
      <div className="p-4 border-b border-white/10 flex items-center justify-between">
        <div>
          <h1 className="text-lg font-display font-bold tracking-tight">Retrion</h1>
          <p className="text-[10px] text-gray-500 tracking-widest uppercase mt-0.5">smart retrieval</p>
        </div>
        <button
          onClick={onClose}
          className="lg:hidden p-1 text-gray-400 hover:text-white rounded"
        >
          <X size={18} />
        </button>
      </div>

      <nav className="p-2 space-y-0.5">
        {navItems.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => onNavigate(id)}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
              activeView === id
                ? 'bg-white/10 text-white font-medium'
                : 'text-gray-400 hover:bg-white/5 hover:text-gray-200'
            }`}
          >
            <Icon size={17} strokeWidth={activeView === id ? 2.2 : 1.8} />
            {label}
          </button>
        ))}
      </nav>

      {activeView === 'chat' && (
        <div className="flex-1 flex flex-col overflow-hidden mt-1 border-t border-white/10">
          <div className="p-2">
            <button
              onClick={onNewSession}
              className="w-full flex items-center justify-center gap-2 px-3 py-2.5 text-sm rounded-lg bg-white/10 hover:bg-white/15 text-white transition-colors font-medium"
            >
              <Plus size={15} />
              New chat
            </button>
          </div>
          <div className="flex-1 overflow-y-auto px-2 space-y-0.5">
            {sessions.map((s) => (
              <div
                key={s.id}
                className={`group flex items-center rounded-lg transition-colors ${
                  currentSession?.id === s.id
                    ? 'bg-white/10 text-white'
                    : 'text-gray-500 hover:bg-white/5 hover:text-gray-300'
                }`}
              >
                <button
                  onClick={() => onSelectSession(s)}
                  className="flex-1 text-left px-3 py-2 text-[13px] truncate"
                >
                  {s.title || 'New conversation'}
                </button>
                <button
                  onClick={(e) => { e.stopPropagation(); onDeleteSession(s.id); }}
                  className="p-1.5 mr-1 text-gray-600 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity shrink-0"
                >
                  <Trash2 size={12} />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="p-3 border-t border-white/10 space-y-1.5">
        <StatusIndicator label="Database" status={health.postgres} />
        <StatusIndicator label="LLM" status={health.llm} />
        <StatusIndicator label="Vectors" status={health.qdrant} />
      </div>
    </aside>
  );
}
