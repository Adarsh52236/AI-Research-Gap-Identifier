import { PageContainer } from '@/components/layout/PageContainer';

export function Library() {
  return (
    <PageContainer>
      <div className="bg-surface rounded-xl shadow-sm border border-border p-8">
        <h2 className="text-2xl font-bold text-text">Library</h2>
        <p className="text-muted mt-2">Browse your indexed research papers and documents.</p>
      </div>
    </PageContainer>
  );
}
