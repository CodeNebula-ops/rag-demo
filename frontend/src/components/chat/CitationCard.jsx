import { useState } from 'react';
import { ChevronDown, ChevronUp, FileText } from 'lucide-react';
import { formatConfidence } from '../../utils/formatters';

export default function CitationCard({ citation }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="border border-[var(--border)] rounded-lg p-3 bg-white">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-start gap-2 text-left"
      >
        <FileText size={16} className="text-accent mt-0.5 flex-shrink-0" />
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-[var(--text-primary)] truncate">
            {citation.document_title}
          </p>
          {citation.section_path && (
            <p className="text-xs text-[var(--text-secondary)] truncate">
              {citation.section_path}
            </p>
          )}
        </div>
        {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
      </button>

      {expanded && (
        <div className="mt-2 pt-2 border-t border-[var(--border)]">
          <p className="text-xs text-[var(--text-secondary)] leading-relaxed">
            {citation.text_snippet}
          </p>
          <div className="mt-2 flex items-center gap-2">
            <div className="flex-1 bg-gray-100 rounded-full h-1.5">
              <div
                className="bg-accent rounded-full h-1.5 transition-all"
                style={{ width: `${Math.round(citation.relevance_score * 100)}%` }}
              />
            </div>
            <span className="text-xs text-[var(--text-secondary)]">
              {formatConfidence(citation.relevance_score)}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
