import { formatConfidence } from '../../utils/formatters';

const config = {
  high: { color: 'text-emerald-700', bg: 'bg-emerald-50', label: 'High' },
  medium: { color: 'text-amber-700', bg: 'bg-amber-50', label: 'Medium' },
  low: { color: 'text-red-600', bg: 'bg-red-50', label: 'Low' },
};

export default function ConfidenceBadge({ score, level }) {
  const effectiveLevel = level || (score >= 0.85 ? 'high' : score >= 0.7 ? 'medium' : 'low');
  const { color, bg, label } = config[effectiveLevel] || config.low;

  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-medium ${color} ${bg}`}>
      {label} {formatConfidence(score)}
    </span>
  );
}
