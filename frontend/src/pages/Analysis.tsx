import { PageContainer } from '@/components/layout/PageContainer';
import { useAnalysis } from '@/features/analysis/hooks/useAnalysis';
import { AnalysisForm } from '@/features/analysis/components/AnalysisForm';
import { AnalysisProgress } from '@/features/analysis/components/AnalysisProgress';
import { AnalysisSummary } from '@/features/analysis/components/AnalysisSummary';
import { TopicList } from '@/features/analysis/components/TopicList';
import { GapList } from '@/features/analysis/components/GapList';
import { InsightCard } from '@/features/analysis/components/InsightCard';
import { DeveloperTools } from '@/features/analysis/components/DeveloperTools';
import { AnalysisHistory } from '@/features/analysis/components/AnalysisHistory';
import { AnalysisHeader } from '@/features/analysis/components/AnalysisHeader';
import { AlertCircle, RefreshCw } from 'lucide-react';
import { useAnalysisStore } from '@/store/analysisStore';
import { useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';

export function Analysis() {
  const [searchParams, setSearchParams] = useSearchParams();
  const projectId = searchParams.get('projectId');
  const initialQuery = searchParams.get('query');
  const navigate = useNavigate();

  const { status, data, error, currentSessionId, runAnalysis, reset } = useAnalysis();

  const handleSubmit = async (query: string, maxResults: number) => {
    const analysisId = await runAnalysis(query, maxResults, projectId || undefined);
    if (projectId && analysisId) {
      navigate(`/analysis/${analysisId}`);
    }
  };

  // Auto-run if we came from Omnibar
  useEffect(() => {
    if (initialQuery && status === 'idle' && projectId) {
      handleSubmit(initialQuery, 100);
      
      // Clean up URL so it doesn't re-trigger on back navigation
      const newParams = new URLSearchParams(searchParams);
      newParams.delete('query');
      setSearchParams(newParams, { replace: true });
    }
  }, [initialQuery, status, projectId, searchParams, setSearchParams]);

  const { sessions } = useAnalysisStore();
  const currentSession = sessions.find(s => s.id === currentSessionId);

  return (
    <PageContainer>
      <div className={`grid grid-cols-1 ${projectId ? 'xl:grid-cols-4' : ''} gap-8`}>
        
        {/* Left Column: History (Only visible if in a project context) */}
        {projectId && (
          <div className="xl:col-span-1">
            <div className="sticky top-6 space-y-6">
              <button
                onClick={reset}
                className="w-full flex items-center justify-center px-4 py-2 border border-primary text-primary hover:bg-blue-50 rounded-lg font-medium transition-colors"
              >
                + New Analysis
              </button>
              <AnalysisHistory projectId={projectId} />
            </div>
          </div>
        )}

        {/* Right Column: Main Content */}
        <div className={projectId ? 'xl:col-span-3' : ''}>
          
          {status === 'idle' && (
            <AnalysisForm onSubmit={handleSubmit} isLoading={false} />
          )}

          {status === 'loading' && (
            <div className="space-y-6">
              <AnalysisForm onSubmit={handleSubmit} isLoading={true} />
              <AnalysisProgress />
            </div>
          )}

          {status === 'error' && error && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
              <div className="bg-red-50 border-l-4 border-red-500 p-6 rounded-r-md shadow-sm">
                <div className="flex items-start">
                  <div className="flex-shrink-0">
                    <AlertCircle className="h-6 w-6 text-red-500" aria-hidden="true" />
                  </div>
                  <div className="ml-4">
                    <h3 className="text-lg font-medium text-red-800">Analysis Failed</h3>
                    <div className="mt-2 text-sm text-red-700">
                      <p>{error.message}</p>
                    </div>
                    <div className="mt-6 flex gap-4">
                      {error.retryable && currentSession && (
                        <button
                          type="button"
                          onClick={() => handleSubmit(currentSession.query, 100)}
                          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                        >
                          <RefreshCw className="w-4 h-4 mr-2" />
                          Retry Now
                        </button>
                      )}
                      <button
                        type="button"
                        onClick={reset}
                        className="inline-flex items-center px-4 py-2 border border-red-300 text-sm font-medium rounded-md text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {status === 'success' && data && currentSession && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
              <AnalysisHeader session={currentSession} />
              
              <AnalysisSummary data={data} />
              
              {data.insights?.map((insight, idx) => (
                <InsightCard key={idx} insight={insight} />
              ))}
              
              <GapList gaps={data.gaps.gaps} />
              
              <TopicList topics={data.topics.topics} />
              
              <DeveloperTools data={data} />
            </div>
          )}

        </div>
      </div>
    </PageContainer>
  );
}
