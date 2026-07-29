import { PageContainer } from '@/components/layout/PageContainer';

export function Projects() {
  return (
    <PageContainer>
      <div className="bg-surface rounded-xl shadow-sm border border-border p-8">
        <h2 className="text-2xl font-bold text-text">Projects</h2>
        <p className="text-muted mt-2">Manage your AI research tracking projects.</p>
      </div>
    </PageContainer>
  );
}
