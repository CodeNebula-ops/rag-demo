import { Menu } from 'lucide-react';

const viewTitles = {
  chat: 'Chat',
  documents: 'Documents',
  analytics: 'Analytics',
};

export default function Header({ activeView, health, onMenuToggle }) {
  const overallOk = health.status === 'ok';

  return (
    <header className="h-14 border-b border-[var(--border)] bg-white flex items-center justify-between px-4 md:px-6 shrink-0">
      <div className="flex items-center gap-3">
        <button
          onClick={onMenuToggle}
          className="lg:hidden p-1.5 -ml-1 text-[var(--text-secondary)] hover:text-[var(--text-primary)] rounded-lg hover:bg-gray-100 transition-colors"
        >
          <Menu size={20} />
        </button>
        <h2 className="text-base font-display font-semibold text-[var(--text-primary)]">
          {viewTitles[activeView]}
        </h2>
      </div>
      <div className="flex items-center gap-2 text-xs text-[var(--text-secondary)]">
        <span
          className={`inline-block w-1.5 h-1.5 rounded-full ${
            overallOk ? 'bg-[var(--success)]' : 'bg-[var(--danger)]'
          }`}
        />
        <span className="hidden sm:inline">
          {overallOk ? 'All systems go' : 'Degraded'}
        </span>
      </div>
    </header>
  );
}
