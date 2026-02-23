import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

// ==================== SEARCH APIs ====================

export const searchPapers = async (query, limit = 10, offset = 0) => {
  const response = await axios.post(`${API_BASE_URL}/search/papers`, {
    query,
    limit,
    offset
  });
  return response.data;
};

export const savePaper = async (paper, topicName) => {
  const response = await axios.post(`${API_BASE_URL}/papers/save`, {
    paper,
    topic_name: topicName
  });
  return response.data;
};

export const getTopics = async () => {
  const response = await axios.get(`${API_BASE_URL}/topics`);
  return response.data;
};

export const getTopicPapers = async (topicId) => {
  const response = await axios.get(`${API_BASE_URL}/topics/${topicId}/papers`);
  return response.data;
};

export const deletePaper = async (paperId) => {
  const response = await axios.delete(`${API_BASE_URL}/papers/${paperId}`);
  return response.data;
};

// ==================== DOCUMENT APIs ====================

export const uploadDocument = async (file, topicId = null) => {
  const formData = new FormData();
  formData.append('file', file);
  if (topicId) {
    formData.append('topic_id', topicId);
  }
  
  const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getDocuments = async (topicId = null) => {
  const url = topicId 
    ? `${API_BASE_URL}/documents?topic_id=${topicId}`
    : `${API_BASE_URL}/documents`;
  const response = await axios.get(url);
  return response.data;
};

export const deleteDocument = async (documentId) => {
  const response = await axios.delete(`${API_BASE_URL}/documents/${documentId}`);
  return response.data;
};

// ==================== CHAT SESSION APIs ====================

export const createSession = async (name, documentIds) => {
  const response = await axios.post(`${API_BASE_URL}/sessions/create`, {
    name,
    document_ids: documentIds
  });
  return response.data;
};

export const getSessions = async () => {
  const response = await axios.get(`${API_BASE_URL}/sessions`);
  return response.data;
};

export const getSessionDetails = async (sessionId) => {
  const response = await axios.get(`${API_BASE_URL}/sessions/${sessionId}`);
  return response.data;
};

export const querySession = async (sessionId, question) => {
  const response = await axios.post(`${API_BASE_URL}/query`, {
    session_id: sessionId,
    question: question,
  });
  return response.data;
};

export const getSessionConversations = async (sessionId) => {
  const response = await axios.get(`${API_BASE_URL}/sessions/${sessionId}/conversations`);
  return response.data;
};

export const deleteSession = async (sessionId) => {
  const response = await axios.delete(`${API_BASE_URL}/sessions/${sessionId}`);
  return response.data;
};