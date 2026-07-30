import { ReactNode } from 'react';
import { AnalysisStoreProvider } from '@/store/analysisStore';
import { ProjectStoreProvider } from '@/features/projects/store/projectStore';
import { AuthProvider } from '@/features/auth/store/AuthContext';

interface AppProvidersProps {
  children: ReactNode;
}

export function AppProviders({ children }: AppProvidersProps) {
  return (
    <AuthProvider>
      <ProjectStoreProvider>
        <AnalysisStoreProvider>
          {children}
        </AnalysisStoreProvider>
      </ProjectStoreProvider>
    </AuthProvider>
  );
}
