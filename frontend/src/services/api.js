import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

export const TOKEN_STORAGE_KEY = 'document_qa_token';
export const USER_STORAGE_KEY = 'document_qa_user';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_STORAGE_KEY);

  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      window.dispatchEvent(new Event('auth:unauthorized'));
    }
    return Promise.reject(error);
  }
);

export const setAuthSession = (token, user) => {
  localStorage.setItem(TOKEN_STORAGE_KEY, token);
  localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user));
};

export const clearAuthSession = () => {
  localStorage.removeItem(TOKEN_STORAGE_KEY);
  localStorage.removeItem(USER_STORAGE_KEY);
};

export const getStoredUser = () => {
  const rawUser = localStorage.getItem(USER_STORAGE_KEY);
  if (!rawUser) {
    return null;
  }

  try {
    return JSON.parse(rawUser);
  } catch {
    clearAuthSession();
    return null;
  }
};

export const loginUser = async (email, password) => {
  const response = await apiClient.post('/auth/login', { email, password });
  return response.data;
};

export const registerUser = async (email, password) => {
  const response = await apiClient.post('/auth/register', { email, password });
  return response.data;
};

export const getCurrentUser = async () => {
  const response = await apiClient.get('/auth/me');
  return response.data;
};

export const searchPapers = async (query, limit = 10, offset = 0) => {
  const response = await apiClient.post('/search/papers', { query, limit, offset });
  return response.data;
};

export const savePaper = async (paper, topicName) => {
  const response = await apiClient.post('/papers/save', {
    paper,
    topic_name: topicName,
  });
  return response.data;
};

export const getTopics = async () => {
  const response = await apiClient.get('/topics');
  return response.data;
};

export const getTopicPapers = async (topicId) => {
  const response = await apiClient.get(`/topics/${topicId}/papers`);
  return response.data;
};

export const deletePaper = async (paperId) => {
  const response = await apiClient.delete(`/papers/${paperId}`);
  return response.data;
};

export const uploadDocument = async (file, topicId = null) => {
  const formData = new FormData();
  formData.append('file', file);

  if (topicId) {
    formData.append('topic_id', topicId);
  }

  const response = await apiClient.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getDocuments = async (topicId = null) => {
  const response = await apiClient.get('/documents', {
    params: topicId ? { topic_id: topicId } : undefined,
  });
  return response.data;
};

export const deleteDocument = async (documentId) => {
  const response = await apiClient.delete(`/documents/${documentId}`);
  return response.data;
};

export const createSession = async (name, documentIds) => {
  const response = await apiClient.post('/sessions/create', {
    name,
    document_ids: documentIds,
  });
  return response.data;
};

export const getSessions = async () => {
  const response = await apiClient.get('/sessions');
  return response.data;
};

export const getSessionDetails = async (sessionId) => {
  const response = await apiClient.get(`/sessions/${sessionId}`);
  return response.data;
};

export const querySession = async (sessionId, question, timeoutMs = 15000) => {
  const token = localStorage.getItem(TOKEN_STORAGE_KEY);
  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(`${API_BASE_URL}/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({
        question,
        session_id: sessionId,
      }),
      signal: controller.signal,
    });

    const data = await response.json();

    if (!response.ok) {
      const requestError = new Error(data?.warning || data?.detail || 'Request failed');
      requestError.response = { data };
      throw requestError;
    }

    return {
      answer: data?.answer || "This question is outside the provided documents.",
      sources: data?.sources || [],
      warning: data?.warning || '',
    };
  } catch (error) {
    if (error.name === 'AbortError') {
      const timeoutError = new Error('Request timeout');
      timeoutError.code = 'REQUEST_TIMEOUT';
      throw timeoutError;
    }

    throw error;
  } finally {
    window.clearTimeout(timeoutId);
  }
};

export const getSessionConversations = async (sessionId) => {
  const response = await apiClient.get(`/sessions/${sessionId}/conversations`);
  return response.data;
};

export const deleteSession = async (sessionId) => {
  const response = await apiClient.delete(`/sessions/${sessionId}`);
  return response.data;
};

export const enableAutoMail = async (payload) => {
  const response = await apiClient.post('/auto-mail/enable', payload);
  return response.data;
};

export const getMailHistory = async (email) => {
  const response = await apiClient.get(`/auto-mail/history/${encodeURIComponent(email)}`);
  return response.data;
};

export default apiClient;
