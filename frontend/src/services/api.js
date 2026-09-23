import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
});

export const apiService = {
  // Document Operations
  async listDocuments() {
    const res = await api.get('/documents');
    return res.data;
  },

  async getDocument(id) {
    const res = await api.get(`/documents/${id}`);
    return res.data;
  },

  async getDocumentChunks(id) {
    const res = await api.get(`/documents/${id}/chunks`);
    return res.data;
  },

  async uploadFile(file, onUploadProgress) {
    const formData = new FormData();
    formData.append('file', file);
    const res = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    });
    return res.data;
  },

  async deleteDocument(id) {
    await api.delete(`/documents/${id}`);
  },

  // Agent Operations
  async chatWithAgent(query, documentId = null, chatHistory = []) {
    const res = await api.post('/agent/chat', {
      query,
      document_id: documentId,
      chat_history: chatHistory,
    });
    return res.data;
  },

  async getSummary(documentId) {
    const res = await api.post('/agent/summary', {
      document_id: documentId,
    });
    return res.data;
  },

  async getChatHistory(documentId) {
    const res = await api.get(`/agent/history/${documentId}`);
    return res.data;
  },

  // Quiz Operations
  async generateQuiz(documentId, numQuestions = 5, difficulty = 'medium') {
    const res = await api.post('/agent/quiz', {
      document_id: documentId,
      num_questions: numQuestions,
      difficulty,
    });
    return res.data;
  },

  async listQuizzes(documentId) {
    const res = await api.get(`/agent/quiz/${documentId}`);
    return res.data;
  },

  // System Health
  async getHealth() {
    const res = await api.get('/health');
    return res.data;
  },
};

export default apiService;
