const viewTitles = {
  chat: 'Chat',
  documents: 'Documents',
  analytics: 'Analytics',
};

export default function Header({ activeView, health }) {
  const overallOk = health.status === 'ok';

  return (
    <header className="h-14 border-b border-[var(--border)] bg-white flex items-center justify-between px-6">
      <h2 className="text-lg font-display font-semibold text-[var(--text-primary)]">
        {viewTitles[activeView] || 'AI Knowledge Base'}
      </h2>
      <div className="flex items-center gap-2 text-sm text-[var(--text-secondary)]">
        <span
          className={`inline-block w-2 h-2 rounded-full ${
            overallOk ? 'bg-[var(--success)]' : 'bg-[var(--danger)]'
          }`}
        />
        {overallOk ? 'All systems operational' : 'Some services degraded'}
      </div>
    </header>
  );
}
