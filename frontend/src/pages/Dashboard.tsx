import { PageContainer } from '@/components/layout/PageContainer';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { Omnibar } from '@/components/Omnibar';

export function Dashboard() {
  const { user } = useAuth();
  
  const firstName = user?.full_name ? user.full_name.split(' ')[0] : user?.username;

  return (
    <PageContainer>
      <div className="flex flex-col items-center justify-center min-h-[70vh] py-12 px-4 sm:px-6 lg:px-8">
        <h1 className="text-4xl sm:text-5xl font-extrabold text-text tracking-tight mb-4 text-center">
          Good morning, {firstName}.
        </h1>
        <p className="text-xl text-muted max-w-2xl text-center mb-12">
          Discover gaps in the literature. Synthesize AI research effortlessly.
        </p>

        <div className="w-full max-w-3xl">
          <Omnibar />
        </div>

        <div className="mt-16 text-center">
          <p className="text-sm font-medium text-muted uppercase tracking-wider mb-6">
            Try these examples
          </p>
          <div className="flex flex-wrap justify-center gap-3">
            {[
              'Federated learning in IoT',
              'Quantum error correction codes',
              'Graph neural networks for drug discovery',
              'RLHF in large language models'
            ].map(example => (
              <span key={example} className="px-4 py-2 rounded-full bg-surface border border-border text-sm text-gray-600 cursor-pointer hover:border-primary hover:text-primary transition-colors">
                {example}
              </span>
            ))}
          </div>
        </div>
      </div>
    </PageContainer>
  );
}
