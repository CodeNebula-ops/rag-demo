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
      <h3 className="text-lg font-display font-semibold mb-3">Upload Document</h3>
      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${
          dragOver
            ? 'border-accent bg-blue-50'
            : 'border-[var(--border)] hover:border-accent/50 hover:bg-gray-50'
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
            <FileText size={32} className="mx-auto text-accent" />
            <p className="text-sm text-[var(--text-secondary)]">Uploading... {progress}%</p>
            <div className="max-w-xs mx-auto bg-gray-100 rounded-full h-2">
              <div
                className="bg-accent rounded-full h-2 transition-all"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        ) : (
          <div className="space-y-2">
            <Upload size={32} className="mx-auto text-[var(--text-secondary)]" />
            <p className="text-sm font-medium text-[var(--text-primary)]">
              Drop a file here or click to upload
            </p>
            <p className="text-xs text-[var(--text-secondary)]">
              PDF, DOCX, TXT, MD (max 50MB)
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
