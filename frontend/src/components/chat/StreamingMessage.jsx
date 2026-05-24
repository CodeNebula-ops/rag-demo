export default function StreamingMessage({ content }) {
  return (
    <div className="flex justify-start">
      <div className="max-w-[75%] rounded-2xl px-4 py-3 bg-[var(--bg-ai-msg)]">
        <p className="text-sm whitespace-pre-wrap">{content}</p>
        <span className="inline-block w-1.5 h-4 bg-accent animate-pulse ml-0.5" />
      </div>
    </div>
  );
}
