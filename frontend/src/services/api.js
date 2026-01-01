import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

export const uploadDocument = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getDocuments = async () => {
  const response = await axios.get(`${API_BASE_URL}/documents`);
  return response.data;
};

export const deleteDocument = async (documentId) => {
  const response = await axios.delete(`${API_BASE_URL}/documents/${documentId}`);
  return response.data;
};

export const queryDocument = async (documentId, question) => {
  const response = await axios.post(`${API_BASE_URL}/query`, {
    document_id: documentId,
    question: question,
  });
  return response.data;
};

export const getConversations = async (documentId) => {
  const response = await axios.get(`${API_BASE_URL}/conversations/${documentId}`);
  return response.data;
};