export default function IngestionProgress({ status, chunks }) {
  if (status !== 'processing') return null;

  return (
    <div className="flex items-center gap-2 text-sm text-[var(--text-secondary)]">
      <div className="w-4 h-4 border-2 border-accent border-t-transparent rounded-full animate-spin" />
      <span>Processing document... {chunks > 0 ? `${chunks} chunks created` : ''}</span>
    </div>
  );
}
