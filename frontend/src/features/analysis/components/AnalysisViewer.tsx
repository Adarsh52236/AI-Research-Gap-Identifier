import { useState, useEffect } from 'react';
import { persistentAnalysisApi, PersistentAnalysis } from '../api/persistentAnalysis';
import { AnalysisHeader } from './AnalysisHeader';
import { AnalysisSummary } from './AnalysisSummary';
import { TopicList } from './TopicList';
import { GapList } from './GapList';
import { InsightCard } from './InsightCard';
import { DeveloperTools } from './DeveloperTools';
import { Loader2 } from 'lucide-react';
import { useParams, useNavigate } from 'react-router-dom';
import { PageContainer } from '@/components/layout/PageContainer';
import { AnalysisResponse, AnalysisSession } from '../types';

export function AnalysisViewer() {
  const { analysisId } = useParams<{ analysisId: string }>();
  const navigate = useNavigate();
  
  const [analysis, setAnalysis] = useState<PersistentAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!analysisId) return;
    
    const fetchAnalysis = async () => {
      try {
        setLoading(true);
        const data = await persistentAnalysisApi.getAnalysis(analysisId);
        setAnalysis(data);
        setError(null);
      } catch (err: any) {
        setError(err.message || 'Failed to load analysis');
      } finally {
        setLoading(false);
      }
    };
    
    fetchAnalysis();
  }, [analysisId]);

  if (loading) {
    return (
      <PageContainer>
        <div className="flex flex-col justify-center items-center py-20 text-gray-400">
          <Loader2 className="w-8 h-8 animate-spin mb-4" />
          <p>Loading analysis...</p>
        </div>
      </PageContainer>
    );
  }

  if (error || !analysis) {
    return (
      <PageContainer>
        <div className="text-center py-20">
          <h2 className="text-xl font-bold text-red-600 mb-2">Analysis Not Found</h2>
          <p className="text-gray-500 mb-6">{error || 'The requested analysis could not be found.'}</p>
          <button 
            onClick={() => navigate(-1)}
            className="text-primary hover:underline font-medium"
          >
            &larr; Go Back
          </button>
        </div>
      </PageContainer>
    );
  }
  
  const rawResponse = analysis.raw_response as AnalysisResponse;

  const mockSession: AnalysisSession = {
    id: analysis.id,
    timestamp: analysis.created_at,
    query: analysis.query,
    status: analysis.status === 'failed' ? 'error' : 'success',
    data: rawResponse,
    metadata: {
      paperCount: analysis.paper_count,
      topicCount: analysis.topic_count,
      gapCount: analysis.gap_count,
      durationSeconds: rawResponse?.duration_seconds || 0
    }
  };

  return (
    <PageContainer>
      <div className="mb-6 flex justify-between items-center">
        <button 
          onClick={() => navigate(-1)}
          className="text-gray-500 hover:text-gray-700 transition-colors text-sm font-medium"
        >
          &larr; Back
        </button>
      </div>

      <article className="max-w-4xl mx-auto bg-white p-8 md:p-12 rounded-2xl shadow-sm border border-gray-100">
        <AnalysisHeader session={mockSession} />
        
        {rawResponse && rawResponse.topics && rawResponse.gaps ? (
          <div className="mt-12 space-y-12 animate-in fade-in slide-in-from-bottom-4 duration-700">
            
            <section className="prose prose-blue max-w-none">
              <AnalysisSummary data={rawResponse} />
            </section>
            
            <hr className="border-gray-100" />
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
              <section>
                <h3 className="text-xl font-bold text-gray-900 mb-6 font-serif">Discovered Topics</h3>
                <TopicList topics={rawResponse.topics.topics} />
              </section>
              <section>
                <h3 className="text-xl font-bold text-gray-900 mb-6 font-serif">Research Gaps</h3>
                <GapList gaps={rawResponse.gaps.gaps} />
              </section>
            </div>
            
            <hr className="border-gray-100" />
            
            <section>
              <h3 className="text-2xl font-bold text-gray-900 mb-6 font-serif">AI Research Insights</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {rawResponse.insights.map((insight, idx) => (
                  <InsightCard key={idx} insight={insight} />
                ))}
              </div>
            </section>

            <DeveloperTools data={rawResponse} />
          </div>
        ) : (
        <div className="mt-8 bg-yellow-50 text-yellow-800 p-6 rounded-xl border border-yellow-200 text-center">
          <p>Analysis raw data is unavailable. The pipeline may have failed or hasn't finished running.</p>
          {analysis.error_message && (
             <p className="mt-4 text-red-600 font-mono text-sm bg-red-50 p-4 rounded-lg text-left">
               {analysis.error_message}
             </p>
          )}
        </div>
      )}
      </article>
    </PageContainer>
  );
}
