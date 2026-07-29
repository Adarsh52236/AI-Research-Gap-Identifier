import { PageContainer } from '@/components/layout/PageContainer';

export function NotFound() {
  return (
    <PageContainer>
      <div className="bg-surface rounded-xl shadow-sm border border-border p-8 text-center">
        <h2 className="text-4xl font-bold text-text mb-4">404</h2>
        <p className="text-muted">The page you are looking for does not exist.</p>
      </div>
    </PageContainer>
  );
}
