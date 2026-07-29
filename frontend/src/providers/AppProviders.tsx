import { ReactNode } from 'react';
import { AnalysisStoreProvider } from '@/store/analysisStore';
import { ProjectStoreProvider } from '@/features/projects/store/projectStore';

interface AppProvidersProps {
  children: ReactNode;
}

export function AppProviders({ children }: AppProvidersProps) {
  return (
    <ProjectStoreProvider>
      <AnalysisStoreProvider>
        {children}
      </AnalysisStoreProvider>
    </ProjectStoreProvider>
  );
}
