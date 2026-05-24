import { useState, useEffect } from 'react';
import { analyticsApi } from '../../services/api';
import { formatConfidence, formatDate } from '../../utils/formatters';

export default function ContentGapsList() {
  const [gaps, setGaps] = useState([]);

  useEffect(() => {
    analyticsApi.contentGaps().then(({ data }) => setGaps(data)).catch(() => {});
  }, []);

  return (
    <div>
      <h3 className="text-lg font-display font-semibold mb-1">Content Gaps</h3>
      <p className="text-sm text-[var(--text-secondary)] mb-3">
        Queries with low confidence scores — consider adding documents to cover these topics.
      </p>

      {gaps.length === 0 ? (
        <p className="text-sm text-[var(--text-secondary)] py-6 text-center bg-white rounded-xl border border-[var(--border)]">
          No content gaps detected yet.
        </p>
      ) : (
        <div className="bg-white rounded-xl border border-[var(--border)] overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[var(--border)] text-left text-[var(--text-secondary)]">
                <th className="px-4 py-3 font-medium">Query</th>
                <th className="px-4 py-3 font-medium w-32">Confidence</th>
                <th className="px-4 py-3 font-medium w-32">Date</th>
              </tr>
            </thead>
            <tbody>
              {gaps.map((gap, i) => (
                <tr key={i} className="border-b border-[var(--border)] last:border-0">
                  <td className="px-4 py-3 truncate max-w-[400px]">{gap.query}</td>
                  <td className="px-4 py-3">
                    <span className="text-[var(--confidence-low)] font-medium">
                      {formatConfidence(gap.confidence_score)}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-[var(--text-secondary)]">
                    {formatDate(gap.created_at)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
