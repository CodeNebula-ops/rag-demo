import { useState, useCallback } from 'react';
import { documentApi } from '../services/api';

export function useDocuments() {
  const [documents, setDocuments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const loadDocuments = useCallback(async () => {
    const { data } = await documentApi.list();
    setDocuments(data);
  }, []);

  const uploadDocument = useCallback(async (file) => {
    setUploading(true);
    setUploadProgress(0);
    try {
      const { data } = await documentApi.upload(file, (event) => {
        const pct = Math.round((event.loaded * 100) / event.total);
        setUploadProgress(pct);
      });

      const pollInterval = setInterval(async () => {
        try {
          const { data: doc } = await documentApi.get(data.id);
          if (doc.status === 'active' || doc.status === 'failed') {
            clearInterval(pollInterval);
            await loadDocuments();
          }
        } catch {
          clearInterval(pollInterval);
        }
      }, 2000);

      await loadDocuments();
      return data;
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  }, [loadDocuments]);

  const deleteDocument = useCallback(async (id) => {
    await documentApi.delete(id);
    await loadDocuments();
  }, [loadDocuments]);

  const reprocessDocument = useCallback(async (id) => {
    await documentApi.reprocess(id);
    await loadDocuments();

    const pollInterval = setInterval(async () => {
      try {
        const { data: doc } = await documentApi.get(id);
        if (doc.status === 'active' || doc.status === 'failed') {
          clearInterval(pollInterval);
          await loadDocuments();
        }
      } catch {
        clearInterval(pollInterval);
      }
    }, 2000);
  }, [loadDocuments]);

  return {
    documents,
    uploading,
    uploadProgress,
    loadDocuments,
    uploadDocument,
    deleteDocument,
    reprocessDocument,
  };
}
