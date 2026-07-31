import { create } from 'zustand';
import { apiClient } from '@/api/client';

export interface ChatSession {
  id: string;
  title: string;
  created_at: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'tool';
  content: string;
  created_at: string;
}

interface ChatState {
  sessions: ChatSession[];
  currentSession: string | null;
  messages: ChatMessage[];
  isLoading: boolean;
  isSending: boolean;
  isResearching: boolean;
  error: string | null;
  fetchSessions: () => Promise<void>;
  fetchMessages: (sessionId: string) => Promise<void>;
  sendMessage: (content: string, sessionId?: string) => Promise<string | undefined>;
  setCurrentSession: (id: string | null) => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  sessions: [],
  currentSession: null,
  messages: [],
  isLoading: false,
  isSending: false,
  isResearching: false,
  error: null,

  setCurrentSession: (id) => set({ currentSession: id, messages: [] }),

  fetchSessions: async () => {
    try {
      set({ isLoading: true, error: null });
      const data = await apiClient<ChatSession[]>('/api/v1/chat/sessions', { method: 'GET' });
      set({ sessions: data });
    } catch (error: any) {
      set({ error: error.message });
    } finally {
      set({ isLoading: false });
    }
  },

  fetchMessages: async (sessionId: string) => {
    try {
      // Clear messages immediately so old session messages don't bleed in
      set({ isLoading: true, error: null, messages: [] });
      const data = await apiClient<ChatMessage[]>(`/api/v1/chat/sessions/${sessionId}/messages`, { method: 'GET' });
      set({ messages: data, currentSession: sessionId });
    } catch (error: any) {
      set({ error: error.message });
    } finally {
      set({ isLoading: false });
    }
  },

  sendMessage: async (content: string, sessionId?: string) => {
    // Track the optimistic message id so we can roll it back on error
    const optimisticId = `optimistic-${Date.now()}`;

    try {
      const looksLikeResearch = /research|analyze|literature|gap|ieee|paper|document/i.test(content);
      set({ isSending: true, isResearching: looksLikeResearch, error: null });

      const optimUserMsg: ChatMessage = {
        id: optimisticId,
        role: 'user',
        content,
        created_at: new Date().toISOString()
      };
      set((state) => ({ messages: [...state.messages, optimUserMsg] }));

      const payload = {
        content,
        session_id: sessionId || null
      };

      const data = await apiClient<any>('/api/v1/chat/message', {
        method: 'POST',
        body: JSON.stringify(payload)
      });

      // Update session if it was new
      if (data.session_id && data.session_id !== get().currentSession) {
        set({ currentSession: data.session_id });
        get().fetchSessions();
      }

      set((state) => ({ messages: [...state.messages, data.message] }));
      return data.session_id;
    } catch (error: any) {
      // Roll back the optimistic message on failure
      set((state) => ({
        messages: state.messages.filter((m) => m.id !== optimisticId),
        error: error.message,
      }));
    } finally {
      set({ isSending: false, isResearching: false });
    }
  }
}));
