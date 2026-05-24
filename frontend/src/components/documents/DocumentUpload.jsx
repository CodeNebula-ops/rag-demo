import { useState, useRef } from 'react';
import { Upload, FileText } from 'lucide-react';

const ACCEPTED = '.pdf,.docx,.doc,.txt,.md';

export default function DocumentUpload({ onUpload, uploading, progress }) {
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef(null);

  const handleFiles = (files) => {
    if (files.length > 0) {
      onUpload(files[0]);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    handleFiles(e.dataTransfer.files);
  };

  return (
    <div>
      <h3 className="text-base font-display font-semibold mb-3">Upload Document</h3>
      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-6 md:p-8 text-center cursor-pointer transition-all ${
          dragOver
            ? 'border-sidebar/40 bg-sidebar/5'
            : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50/50'
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPTED}
          onChange={(e) => handleFiles(e.target.files)}
          className="hidden"
        />
        {uploading ? (
          <div className="space-y-2">
            <FileText size={28} className="mx-auto text-sidebar animate-pulse" />
            <p className="text-sm text-[var(--text-secondary)]">
              {progress < 100 ? `Uploading... ${progress}%` : 'Processing document...'}
            </p>
            <div className="max-w-xs mx-auto bg-gray-100 rounded-full h-1.5">
              <div
                className="bg-sidebar rounded-full h-1.5 transition-all"
                style={{ width: progress < 100 ? `${progress}%` : '100%' }}
              />
            </div>
          </div>
        ) : (
          <div className="space-y-1.5">
            <Upload size={28} className="mx-auto text-gray-300" />
            <p className="text-sm font-medium text-[var(--text-primary)]">
              Drop a file or click to browse
            </p>
            <p className="text-xs text-gray-400">
              PDF, DOCX, TXT, MD up to 50MB
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
