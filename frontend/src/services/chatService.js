import api from './api';

export const chatService = {
  getSessions: async () => {
    const res = await api.get('/chat/sessions');
    return res.data;
  },

  createSession: async (title) => {
    const res = await api.post('/chat/sessions', { title });
    return res.data;
  },

  updateSession: async (sessionId, title) => {
    const res = await api.put(`/chat/sessions/${sessionId}`, { title });
    return res.data;
  },

  deleteSession: async (sessionId) => {
    const res = await api.delete(`/chat/sessions/${sessionId}`);
    return res.data;
  },

  getMessages: async (sessionId) => {
    const res = await api.get(`/chat/sessions/${sessionId}/messages`);
    return res.data;
  },

  createMessage: async (sessionId, role, content, run_id = null) => {
    const res = await api.post(`/chat/sessions/${sessionId}/messages`, {
      role,
      content,
      run_id
    });
    return res.data;
  },

  orchestrateChat: async (sessionId, payload) => {
    const res = await api.post(`/chat/sessions/${sessionId}/orchestrate`, payload);
    return res.data;
  }
};
