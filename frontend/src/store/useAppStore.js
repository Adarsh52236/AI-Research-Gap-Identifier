import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const useAppStore = create(
  persist(
    (set, get) => ({
      ui: {
        sidebarCollapsed: false,
        theme: 'light',
      },
      setUI: (uiUpdates) => set((state) => ({ ui: { ...state.ui, ...uiUpdates } })),
      
      auth: {
        token: null,
        user: null,
      },
      login: (token, user) => set({ auth: { token, user } }),
      logout: () => set({ auth: { token: null, user: null }, runs: [], messagesByRunId: {} }),
      
      runs: [],
      setRuns: (runs) => set({ runs }),
      addRun: (run) => set((state) => {
        // Prevent duplicates
        if (state.runs.find(r => r.run_id === run.run_id)) return state;
        return { runs: [run, ...state.runs] };
      }),
      updateRun: (runId, updates) => set((state) => ({
        runs: state.runs.map(r => r.run_id === runId ? { ...r, ...updates } : r)
      })),

      activeRunId: null,
      setActiveRunId: (id) => set({ activeRunId: id }),

      messagesByRunId: {},
      addMessage: (runId, message) => set((state) => ({
        messagesByRunId: {
          ...state.messagesByRunId,
          [runId]: [...(state.messagesByRunId[runId] || []), message]
        }
      })),
      updateMessage: (runId, messageId, content) => set((state) => {
        const runMessages = state.messagesByRunId[runId] || [];
        return {
          messagesByRunId: {
            ...state.messagesByRunId,
            [runId]: runMessages.map(m => m.id === messageId ? { ...m, content } : m)
          }
        };
      }),
      
      debugState: {
        lastRequest: null,
        lastPollStatus: null,
        lastError: null,
      },
      setDebugState: (updates) => set((state) => ({ 
        debugState: { ...state.debugState, ...updates } 
      }))
    }),
    {
      name: 'research-gap-storage',
    }
  )
);

export default useAppStore;
