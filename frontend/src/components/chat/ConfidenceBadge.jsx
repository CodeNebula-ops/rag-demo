import { formatConfidence } from '../../utils/formatters';

const config = {
  high: {
    color: 'text-[var(--confidence-high)]',
    bg: 'bg-green-50',
    label: 'High confidence',
  },
  medium: {
    color: 'text-[var(--confidence-medium)]',
    bg: 'bg-yellow-50',
    label: 'Medium confidence',
  },
  low: {
    color: 'text-[var(--confidence-low)]',
    bg: 'bg-red-50',
    label: 'Low confidence',
  },
};

export default function ConfidenceBadge({ score, level }) {
  const effectiveLevel = level || (score >= 0.85 ? 'high' : score >= 0.7 ? 'medium' : 'low');
  const { color, bg, label } = config[effectiveLevel] || config.low;

  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${color} ${bg}`}
      title={`Confidence score: ${formatConfidence(score)}. ${
        effectiveLevel === 'low'
          ? 'This answer may be incomplete. Please verify with the source document.'
          : ''
      }`}
    >
      <span
        className={`w-1.5 h-1.5 rounded-full ${
          effectiveLevel === 'high'
            ? 'bg-[var(--confidence-high)]'
            : effectiveLevel === 'medium'
            ? 'bg-[var(--confidence-medium)]'
            : 'bg-[var(--confidence-low)]'
        }`}
      />
      {label} ({formatConfidence(score)})
    </span>
  );
}
