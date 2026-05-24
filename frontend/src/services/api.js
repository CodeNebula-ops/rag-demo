import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

export const chatApi = {
  createSession: (title) => api.post('/chat/sessions', { title }),
  listSessions: () => api.get('/chat/sessions'),
  getHistory: (sessionId) => api.get(`/chat/sessions/${sessionId}/history`),
  submitFeedback: (messageId, feedback) =>
    api.post(`/chat/messages/${messageId}/feedback`, { feedback }),
};

export const documentApi = {
  upload: (file, onProgress) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/documents', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: onProgress,
    });
  },
  list: () => api.get('/documents'),
  get: (id) => api.get(`/documents/${id}`),
  delete: (id) => api.delete(`/documents/${id}`),
  reprocess: (id) => api.post(`/documents/${id}/reprocess`),
};

export const analyticsApi = {
  usage: () => api.get('/analytics/usage'),
  contentGaps: () => api.get('/analytics/content-gaps'),
};

export const healthApi = {
  check: () => api.get('/health'),
};

export function getStreamUrl(sessionId) {
  return `${BASE_URL}/chat/sessions/${sessionId}/messages`;
}

export default api;
