export default function StatusIndicator({ label, status }) {
  const colors = {
    ok: 'bg-[var(--success)]',
    error: 'bg-[var(--danger)]',
    checking: 'bg-yellow-400 animate-pulse',
  };

  return (
    <div className="flex items-center gap-2 text-xs text-gray-400">
      <span className={`w-1.5 h-1.5 rounded-full ${colors[status] || colors.error}`} />
      {label}
    </div>
  );
}
