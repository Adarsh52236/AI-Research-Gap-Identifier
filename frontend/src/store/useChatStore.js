import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { chatService } from '../services/chatService';

const useChatStore = create(
  devtools(
    (set, get) => ({
      sessions: [],
      activeSessionId: null,
      messagesBySessionId: {},
      isFetchingSessions: false,
      isFetchingMessages: false,

      setActiveSessionId: (id) => set({ activeSessionId: id }),

      fetchSessions: async () => {
        set({ isFetchingSessions: true });
        try {
          const sessions = await chatService.getSessions();
          set({ sessions });
        } catch (error) {
          console.error("Failed to fetch sessions", error);
        } finally {
          set({ isFetchingSessions: false });
        }
      },

      createSession: async (title = "New Chat") => {
        try {
          const newSession = await chatService.createSession(title);
          set((state) => ({
            sessions: [newSession, ...state.sessions],
            activeSessionId: newSession.id,
          }));
          return newSession;
        } catch (error) {
          console.error("Failed to create session", error);
          throw error;
        }
      },

      updateSessionTitle: async (sessionId, title) => {
        try {
          const updatedSession = await chatService.updateSession(sessionId, title);
          set((state) => ({
            sessions: state.sessions.map(s => s.id === sessionId ? updatedSession : s)
          }));
        } catch (error) {
          console.error("Failed to update session title", error);
        }
      },

      deleteSession: async (sessionId) => {
        try {
          await chatService.deleteSession(sessionId);
          set((state) => {
            const newSessions = state.sessions.filter(s => s.id !== sessionId);
            const newMessages = { ...state.messagesBySessionId };
            delete newMessages[sessionId];
            
            return {
              sessions: newSessions,
              messagesBySessionId: newMessages,
              activeSessionId: state.activeSessionId === sessionId ? null : state.activeSessionId
            };
          });
        } catch (error) {
          console.error("Failed to delete session", error);
        }
      },

      fetchMessages: async (sessionId) => {
        set({ isFetchingMessages: true });
        try {
          const messages = await chatService.getMessages(sessionId);
          set((state) => ({
            messagesBySessionId: {
              ...state.messagesBySessionId,
              [sessionId]: messages
            }
          }));
        } catch (error) {
          console.error(`Failed to fetch messages for session ${sessionId}`, error);
        } finally {
          set({ isFetchingMessages: false });
        }
      },

      addLocalMessage: (sessionId, message) => {
        set((state) => {
          const existing = state.messagesBySessionId[sessionId] || [];
          // Avoid duplicates by ID
          if (existing.some(m => m.id === message.id)) {
            return state;
          }
          return {
            messagesBySessionId: {
              ...state.messagesBySessionId,
              [sessionId]: [...existing, message]
            }
          };
        });
      },

      updateLocalMessage: (sessionId, messageId, updates) => {
         set((state) => {
           const existing = state.messagesBySessionId[sessionId] || [];
           return {
             messagesBySessionId: {
               ...state.messagesBySessionId,
               [sessionId]: existing.map(m => m.id === messageId ? { ...m, ...updates } : m)
             }
           };
         });
      },
      
      clearStore: () => set({
         sessions: [],
         activeSessionId: null,
         messagesBySessionId: {}
      })
    }),
    { name: 'ChatStore' }
  )
);

export default useChatStore;
