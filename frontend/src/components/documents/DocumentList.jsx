import { useState } from 'react';
import { Trash2, RefreshCw } from 'lucide-react';
import { formatDate, formatFileSize } from '../../utils/formatters';

const statusStyles = {
  processing: 'bg-yellow-100 text-yellow-800 animate-pulse',
  active: 'bg-green-100 text-green-800',
  archived: 'bg-gray-100 text-gray-600',
  failed: 'bg-red-100 text-red-800',
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
        <h3 className="text-lg font-display font-semibold">Documents ({documents.length})</h3>
        <button
          onClick={onRefresh}
          className="p-2 text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
          title="Refresh"
        >
          <RefreshCw size={16} />
        </button>
      </div>

      {documents.length === 0 ? (
        <p className="text-sm text-[var(--text-secondary)] py-8 text-center">
          No documents uploaded yet. Upload a document to get started.
        </p>
      ) : (
        <div className="bg-white rounded-xl border border-[var(--border)] overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[var(--border)] text-left text-[var(--text-secondary)]">
                <th className="px-4 py-3 font-medium">Title</th>
                <th className="px-4 py-3 font-medium">Type</th>
                <th className="px-4 py-3 font-medium">Size</th>
                <th className="px-4 py-3 font-medium">Chunks</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Uploaded</th>
                <th className="px-4 py-3 font-medium w-16"></th>
              </tr>
            </thead>
            <tbody>
              {documents.map((doc) => (
                <tr key={doc.id} className="border-b border-[var(--border)] last:border-0 hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium truncate max-w-[200px]">{doc.title}</td>
                  <td className="px-4 py-3 uppercase text-xs text-[var(--text-secondary)]">{doc.file_type}</td>
                  <td className="px-4 py-3 text-[var(--text-secondary)]">{formatFileSize(doc.file_size_bytes)}</td>
                  <td className="px-4 py-3">{doc.total_chunks}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${statusStyles[doc.status] || ''}`}>
                      {doc.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-[var(--text-secondary)]">{formatDate(doc.created_at)}</td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() => handleDelete(doc.id)}
                      className={`p-1 rounded transition-colors ${
                        confirmId === doc.id
                          ? 'text-[var(--danger)] bg-red-50'
                          : 'text-gray-300 hover:text-[var(--danger)]'
                      }`}
                      title={confirmId === doc.id ? 'Click again to confirm' : 'Delete'}
                    >
                      <Trash2 size={14} />
                    </button>
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
