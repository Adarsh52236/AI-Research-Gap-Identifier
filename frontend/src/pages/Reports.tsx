import { PageContainer } from '@/components/layout/PageContainer';

export function Reports() {
  return (
    <PageContainer>
      <div className="bg-surface rounded-xl shadow-sm border border-border p-8">
        <h2 className="text-2xl font-bold text-text">Reports</h2>
        <p className="text-muted mt-2">View and export generated research insights.</p>
      </div>
    </PageContainer>
  );
}
