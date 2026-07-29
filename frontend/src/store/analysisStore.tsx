import { createContext, useContext, useState, ReactNode, useCallback } from 'react';
import { AnalysisSession } from '@/features/analysis/types';

interface AnalysisStoreContextType {
  sessions: AnalysisSession[];
  addSession: (session: AnalysisSession) => void;
  clearSessions: () => void;
}

const AnalysisStoreContext = createContext<AnalysisStoreContextType | undefined>(undefined);

export function AnalysisStoreProvider({ children }: { children: ReactNode }) {
  const [sessions, setSessions] = useState<AnalysisSession[]>([]);

  const addSession = useCallback((session: AnalysisSession) => {
    setSessions((prev) => [session, ...prev]);
  }, []);

  const clearSessions = useCallback(() => {
    setSessions([]);
  }, []);

  return (
    <AnalysisStoreContext.Provider value={{ sessions, addSession, clearSessions }}>
      {children}
    </AnalysisStoreContext.Provider>
  );
}

export function useAnalysisStore() {
  const context = useContext(AnalysisStoreContext);
  if (context === undefined) {
    throw new Error('useAnalysisStore must be used within an AnalysisStoreProvider');
  }
  return context;
}
