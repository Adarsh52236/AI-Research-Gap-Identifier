import { PageContainer } from '@/components/layout/PageContainer';

export function Settings() {
  return (
    <PageContainer>
      <div className="bg-surface rounded-xl shadow-sm border border-border p-8">
        <h2 className="text-2xl font-bold text-text">Settings</h2>
        <p className="text-muted mt-2">Manage your ResearchOS preferences and system configuration.</p>
      </div>
    </PageContainer>
  );
}
