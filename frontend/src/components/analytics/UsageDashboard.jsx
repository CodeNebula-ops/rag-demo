import { useState, useEffect } from 'react';
import { analyticsApi } from '../../services/api';
import { formatConfidence, formatLatency } from '../../utils/formatters';

export default function UsageDashboard() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    analyticsApi.usage().then(({ data }) => setStats(data)).catch(() => {});
  }, []);

  if (!stats) {
    return <div className="text-sm text-gray-400">Loading...</div>;
  }

  const cards = [
    { label: 'Total Queries', value: stats.total_queries },
    { label: 'Today', value: stats.queries_today },
    { label: 'Avg Confidence', value: formatConfidence(stats.avg_confidence) },
    { label: 'Avg Latency', value: formatLatency(stats.avg_latency_ms) },
  ];

  return (
    <div>
      <h3 className="text-base font-display font-semibold mb-3">Overview</h3>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {cards.map(({ label, value }) => (
          <div
            key={label}
            className="bg-white rounded-xl border border-[var(--border)] p-4"
          >
            <p className="text-[11px] text-gray-400 uppercase tracking-wider">{label}</p>
            <p className="text-xl font-display font-bold mt-1">{value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
