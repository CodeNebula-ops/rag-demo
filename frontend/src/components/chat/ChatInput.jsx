import { useState, useRef, useEffect } from 'react';
import { ArrowUp } from 'lucide-react';

export default function ChatInput({ onSend, disabled }) {
  const [text, setText] = useState('');
  const textareaRef = useRef(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [text]);

  const handleSubmit = () => {
    const trimmed = text.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setText('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="border-t border-[var(--border)] bg-white p-3 md:p-4">
      <div className="max-w-3xl mx-auto flex items-end gap-2">
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={text}
            onChange={(e) => setText(e.target.value.slice(0, 2000))}
            onKeyDown={handleKeyDown}
            placeholder="Ask something..."
            disabled={disabled}
            rows={1}
            className="w-full resize-none rounded-xl border border-[var(--border)] px-4 py-3 pr-16 text-sm focus:outline-none focus:ring-2 focus:ring-sidebar/20 focus:border-sidebar/40 disabled:opacity-50 disabled:bg-gray-50 placeholder:text-gray-400"
          />
          <span className="absolute right-12 bottom-3.5 text-[10px] text-gray-300">
            {text.length > 0 && `${text.length}/2k`}
          </span>
        </div>
        <button
          onClick={handleSubmit}
          disabled={disabled || !text.trim()}
          className="p-2.5 rounded-xl bg-sidebar hover:bg-[#252547] text-white transition-colors disabled:opacity-30 disabled:cursor-not-allowed shrink-0"
        >
          <ArrowUp size={18} />
        </button>
      </div>
    </div>
  );
}
