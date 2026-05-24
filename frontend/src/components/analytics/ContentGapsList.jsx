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
      <h3 className="text-base font-display font-semibold mb-1">Content Gaps</h3>
      <p className="text-xs text-gray-400 mb-3">
        Low-confidence queries that could use more documentation.
      </p>

      {gaps.length === 0 ? (
        <p className="text-sm text-gray-400 py-6 text-center bg-white rounded-xl border border-[var(--border)]">
          No gaps detected yet.
        </p>
      ) : (
        <>
          {/* Desktop */}
          <div className="hidden md:block bg-white rounded-xl border border-[var(--border)] overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--border)] text-left text-gray-400">
                  <th className="px-4 py-3 font-medium">Query</th>
                  <th className="px-4 py-3 font-medium w-28">Confidence</th>
                  <th className="px-4 py-3 font-medium w-28">Date</th>
                </tr>
              </thead>
              <tbody>
                {gaps.map((gap, i) => (
                  <tr key={i} className="border-b border-[var(--border)] last:border-0">
                    <td className="px-4 py-3 truncate max-w-[400px]">{gap.query}</td>
                    <td className="px-4 py-3">
                      <span className="text-red-500 font-medium text-xs">
                        {formatConfidence(gap.confidence_score)}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-400 text-xs">{formatDate(gap.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Mobile */}
          <div className="md:hidden space-y-2">
            {gaps.map((gap, i) => (
              <div key={i} className="bg-white rounded-xl border border-[var(--border)] p-3">
                <p className="text-sm truncate">{gap.query}</p>
                <div className="flex items-center gap-3 mt-1.5">
                  <span className="text-red-500 text-xs font-medium">{formatConfidence(gap.confidence_score)}</span>
                  <span className="text-gray-400 text-xs">{formatDate(gap.created_at)}</span>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
