import { useState, useEffect, useCallback } from 'react';
import { persistentAnalysisApi, PersistentAnalysis } from '../api/persistentAnalysis';
import { AnalysisHistoryCard } from './AnalysisHistoryCard';
import { Link } from 'react-router-dom';
import { Loader2 } from 'lucide-react';
import { DeleteAnalysisDialog } from './DeleteAnalysisDialog';

interface AnalysisHistoryProps {
  projectId: string;
}

export function AnalysisHistory({ projectId }: AnalysisHistoryProps) {
  const [analyses, setAnalyses] = useState<PersistentAnalysis[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deleteId, setDeleteId] = useState<string | null>(null);

  const fetchAnalyses = useCallback(async () => {
    try {
      setLoading(true);
      const data = await persistentAnalysisApi.listProjectAnalyses(projectId);
      setAnalyses(data);
      setError(null);
    } catch (err: any) {
      setError(err.message || 'Failed to load analyses');
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    fetchAnalyses();
  }, [fetchAnalyses]);

  const handleDelete = async () => {
    if (!deleteId) return;
    try {
      await persistentAnalysisApi.deleteAnalysis(deleteId);
      await fetchAnalyses();
      setDeleteId(null);
    } catch (err: any) {
      console.error('Failed to delete analysis:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12 text-gray-400 bg-surface border border-border rounded-xl shadow-sm">
        <Loader2 className="w-6 h-6 animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8 text-red-500 bg-red-50 rounded-lg">
        <p>{error}</p>
      </div>
    );
  }

  if (analyses.length === 0) {
    return (
      <div className="text-center py-12 border-2 border-dashed border-gray-200 rounded-lg bg-surface">
        <p className="text-gray-500 mb-2">No analyses have been saved to this project yet.</p>
        <Link to={`/analysis?projectId=${projectId}`} className="text-primary hover:underline font-medium text-sm">
          Run your first analysis &rarr;
        </Link>
      </div>
    );
  }

  return (
    <>
      <div className="space-y-4">
        {analyses.map(analysis => (
          <AnalysisHistoryCard 
            key={analysis.id} 
            analysis={analysis} 
            onDelete={() => setDeleteId(analysis.id)} 
          />
        ))}
      </div>
      
      {deleteId && (
        <DeleteAnalysisDialog 
          isOpen={true} 
          onClose={() => setDeleteId(null)} 
          onConfirm={handleDelete} 
        />
      )}
    </>
  );
}
