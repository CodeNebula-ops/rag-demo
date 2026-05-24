import { useState, useCallback, useRef } from 'react';
import { chatApi, getStreamUrl } from '../services/api';

export function useChat() {
  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const abortRef = useRef(null);

  const loadSessions = useCallback(async () => {
    const { data } = await chatApi.listSessions();
    setSessions(data);
  }, []);

  const createSession = useCallback(async () => {
    const { data } = await chatApi.createSession(null);
    setCurrentSession(data);
    setMessages([]);
    await loadSessions();
    return data;
  }, [loadSessions]);

  const selectSession = useCallback(async (session) => {
    setCurrentSession(session);
    const { data } = await chatApi.getHistory(session.id);
    setMessages(data);
  }, []);

  const sendMessage = useCallback(async (query) => {
    if (!currentSession || isStreaming) return;

    const userMsg = {
      id: crypto.randomUUID(),
      role: 'user',
      content: query,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsStreaming(true);

    const assistantMsg = {
      id: 'streaming',
      role: 'assistant',
      content: '',
      citations: null,
      confidence_score: null,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, assistantMsg]);

    try {
      const response = await fetch(
        getStreamUrl(currentSession.id),
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query }),
        }
      );

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('event:')) {
            const eventType = line.slice(6).trim();
            continue;
          }
          if (!line.startsWith('data:')) continue;

          const jsonStr = line.slice(5).trim();
          if (!jsonStr) continue;

          try {
            const data = JSON.parse(jsonStr);
            const eventLine = lines.find((l) => l.startsWith('event:'));

            if (data.token !== undefined) {
              setMessages((prev) => {
                const updated = [...prev];
                const last = updated[updated.length - 1];
                if (last && last.id === 'streaming') {
                  updated[updated.length - 1] = {
                    ...last,
                    content: last.content + data.token,
                  };
                }
                return updated;
              });
            }

            if (data.citations) {
              setMessages((prev) => {
                const updated = [...prev];
                const last = updated[updated.length - 1];
                if (last && last.id === 'streaming') {
                  updated[updated.length - 1] = { ...last, citations: data.citations };
                }
                return updated;
              });
            }

            if (data.score !== undefined && data.level !== undefined) {
              setMessages((prev) => {
                const updated = [...prev];
                const last = updated[updated.length - 1];
                if (last && last.id === 'streaming') {
                  updated[updated.length - 1] = {
                    ...last,
                    confidence_score: data.score,
                    confidence_level: data.level,
                  };
                }
                return updated;
              });
            }

            if (data.message_id) {
              setMessages((prev) => {
                const updated = [...prev];
                const last = updated[updated.length - 1];
                if (last && last.id === 'streaming') {
                  updated[updated.length - 1] = {
                    ...last,
                    id: data.message_id,
                    latency_ms: data.latency_ms,
                  };
                }
                return updated;
              });
            }
          } catch {}
        }
      }
    } catch (err) {
      setMessages((prev) => {
        const updated = [...prev];
        const last = updated[updated.length - 1];
        if (last && last.id === 'streaming') {
          updated[updated.length - 1] = {
            ...last,
            id: crypto.randomUUID(),
            content: 'Failed to get response. Please try again.',
          };
        }
        return updated;
      });
    } finally {
      setIsStreaming(false);
    }
  }, [currentSession, isStreaming]);

  const submitFeedback = useCallback(async (messageId, feedback) => {
    await chatApi.submitFeedback(messageId, feedback);
    setMessages((prev) =>
      prev.map((m) => (m.id === messageId ? { ...m, feedback } : m))
    );
  }, []);

  return {
    sessions,
    currentSession,
    messages,
    isStreaming,
    loadSessions,
    createSession,
    selectSession,
    sendMessage,
    submitFeedback,
  };
}
