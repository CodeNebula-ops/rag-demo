import { useState, useCallback } from 'react';
import { documentApi } from '../services/api';
import { useToast } from '../components/layout/Toast';

export function useDocuments() {
  const [documents, setDocuments] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const toast = useToast();

  const loadDocuments = useCallback(async () => {
    try {
      const { data } = await documentApi.list();
      setDocuments(data);
    } catch {
      toast?.('Failed to load documents', 'error');
    }
  }, [toast]);

  const uploadDocument = useCallback(async (file) => {
    setUploading(true);
    setUploadProgress(0);
    try {
      await documentApi.upload(file, (event) => {
        const pct = Math.round((event.loaded * 100) / event.total);
        setUploadProgress(pct);
      });
      toast?.('Document processed successfully', 'success');
      await loadDocuments();
    } catch (err) {
      const msg = err.response?.data?.detail || 'Upload failed';
      toast?.(msg, 'error', 8000);
      await loadDocuments();
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  }, [loadDocuments, toast]);

  const deleteDocument = useCallback(async (id) => {
    try {
      await documentApi.delete(id);
      toast?.('Document deleted', 'success');
      await loadDocuments();
    } catch {
      toast?.('Failed to delete document', 'error');
    }
  }, [loadDocuments, toast]);

  const reprocessDocument = useCallback(async (id) => {
    try {
      const { data } = await documentApi.reprocess(id);
      toast?.(`Document processed: ${data.chunks} chunks`, 'success');
      await loadDocuments();
    } catch (err) {
      const msg = err.response?.data?.detail || 'Reprocess failed';
      toast?.(msg, 'error', 8000);
      await loadDocuments();
    }
  }, [loadDocuments, toast]);

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
