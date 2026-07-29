import { PageContainer } from '@/components/layout/PageContainer';

export function Dashboard() {
  return (
    <PageContainer>
      <div className="bg-surface rounded-xl shadow-sm border border-border p-8">
        <h2 className="text-2xl font-bold text-text">Dashboard</h2>
        <p className="text-muted mt-2">Welcome back. Here's an overview of your research intelligence.</p>
      </div>
    </PageContainer>
  );
}
