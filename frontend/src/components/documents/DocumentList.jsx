import { useState } from 'react';
import { Trash2, RefreshCw, FileText } from 'lucide-react';
import { formatDate, formatFileSize } from '../../utils/formatters';

const statusStyles = {
  processing: 'bg-amber-50 text-amber-700 animate-pulse',
  active: 'bg-emerald-50 text-emerald-700',
  archived: 'bg-gray-100 text-gray-500',
  failed: 'bg-red-50 text-red-600',
};

export default function DocumentList({ documents, onDelete, onRefresh }) {
  const [confirmId, setConfirmId] = useState(null);

  const handleDelete = async (id) => {
    if (confirmId === id) {
      await onDelete(id);
      setConfirmId(null);
    } else {
      setConfirmId(id);
      setTimeout(() => setConfirmId(null), 3000);
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-base font-display font-semibold">Documents ({documents.length})</h3>
        <button
          onClick={onRefresh}
          className="p-2 text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
        >
          <RefreshCw size={15} />
        </button>
      </div>

      {documents.length === 0 ? (
        <p className="text-sm text-[var(--text-secondary)] py-8 text-center">
          No documents yet. Upload one above to get started.
        </p>
      ) : (
        <>
          {/* Desktop table */}
          <div className="hidden md:block bg-white rounded-xl border border-[var(--border)] overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--border)] text-left text-[var(--text-secondary)]">
                  <th className="px-4 py-3 font-medium">Title</th>
                  <th className="px-4 py-3 font-medium">Type</th>
                  <th className="px-4 py-3 font-medium">Size</th>
                  <th className="px-4 py-3 font-medium">Chunks</th>
                  <th className="px-4 py-3 font-medium">Status</th>
                  <th className="px-4 py-3 font-medium">Uploaded</th>
                  <th className="px-4 py-3 font-medium w-12"></th>
                </tr>
              </thead>
              <tbody>
                {documents.map((doc) => (
                  <tr key={doc.id} className="border-b border-[var(--border)] last:border-0 hover:bg-gray-50/50">
                    <td className="px-4 py-3 font-medium truncate max-w-[200px]">{doc.title}</td>
                    <td className="px-4 py-3 uppercase text-[11px] text-[var(--text-secondary)] tracking-wide">{doc.file_type}</td>
                    <td className="px-4 py-3 text-[var(--text-secondary)]">{formatFileSize(doc.file_size_bytes)}</td>
                    <td className="px-4 py-3">{doc.total_chunks}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded-md text-[11px] font-medium ${statusStyles[doc.status] || ''}`}>
                        {doc.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-[var(--text-secondary)] text-xs">{formatDate(doc.created_at)}</td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() => handleDelete(doc.id)}
                        className={`p-1 rounded transition-colors ${
                          confirmId === doc.id
                            ? 'text-red-500 bg-red-50'
                            : 'text-gray-300 hover:text-red-400'
                        }`}
                      >
                        <Trash2 size={14} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Mobile cards */}
          <div className="md:hidden space-y-2">
            {documents.map((doc) => (
              <div key={doc.id} className="bg-white rounded-xl border border-[var(--border)] p-3.5">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2.5 min-w-0">
                    <FileText size={16} className="text-gray-400 shrink-0" />
                    <div className="min-w-0">
                      <p className="text-sm font-medium truncate">{doc.title}</p>
                      <p className="text-[11px] text-gray-400 mt-0.5">
                        {doc.file_type.toUpperCase()} · {formatFileSize(doc.file_size_bytes)} · {doc.total_chunks} chunks
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <span className={`px-2 py-0.5 rounded-md text-[10px] font-medium ${statusStyles[doc.status] || ''}`}>
                      {doc.status}
                    </span>
                    <button
                      onClick={() => handleDelete(doc.id)}
                      className={`p-1 rounded ${
                        confirmId === doc.id ? 'text-red-500' : 'text-gray-300'
                      }`}
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
