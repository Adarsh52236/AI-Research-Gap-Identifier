import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import useAppStore from '../store/useAppStore';
import { mineGapSignals, indexEmbeddings, generateGapReport } from '../services/analysisService';

export default function Analysis() {
  const { selectedPaperIds, query, setReport } = useAppStore();
  const navigate = useNavigate();
  
  const [status, setStatus] = useState({
    mined: false,
    indexed: false,
  });
  const [loading, setLoading] = useState('');
  const [error, setError] = useState(null);

  const handleMine = async () => {
    setLoading('mining');
    setError(null);
    try {
      await mineGapSignals(selectedPaperIds);
      setStatus(prev => ({ ...prev, mined: true }));
    } catch (err) {
      setError('Failed to mine signals: ' + err.message);
    } finally {
      setLoading('');
    }
  };

  const handleIndex = async () => {
    setLoading('indexing');
    setError(null);
    try {
      await indexEmbeddings(selectedPaperIds);
      setStatus(prev => ({ ...prev, indexed: true }));
    } catch (err) {
      setError('Failed to index embeddings: ' + err.message);
    } finally {
      setLoading('');
    }
  };

  const handleReport = async () => {
    setLoading('reporting');
    setError(null);
    try {
      const res = await generateGapReport(selectedPaperIds, query || 'AI research gaps');
      setReport(res.report);
      navigate('/dashboard');
    } catch (err) {
      setError('Failed to generate report: ' + err.message);
    } finally {
      setLoading('');
    }
  };

  if (selectedPaperIds.length === 0) {
    return (
      <div className="max-w-2xl mx-auto mt-10 p-6 bg-panel shadow-sm border border-border rounded text-center">
        <h2 className="text-xl mb-4 text-text">No papers selected for analysis.</h2>
        <Link to="/results" className="text-accent hover:underline">Go back to Results</Link>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-text mb-2">Analysis Pipeline</h1>
        <p className="text-muted">
          Running analysis on {selectedPaperIds.length} paper(s). Execute the steps sequentially or skip to the report if already processed previously.
        </p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-900/20 text-red-400 rounded border border-red-500/50">
          {error}
        </div>
      )}

      <div className="space-y-6">
        {/* Mine Step */}
        <div className="border border-border rounded p-5 bg-panel shadow-sm flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-lg text-text">1. Mine Gap Signals</h3>
            <p className="text-sm text-muted">Extract sentence-level research gap evidence.</p>
          </div>
          <button 
            onClick={handleMine}
            disabled={loading !== '' || status.mined}
            className="bg-accent/20 text-accent px-4 py-2 rounded hover:bg-accent/30 font-medium disabled:opacity-50 min-w-[120px]"
          >
            {loading === 'mining' ? 'Working...' : (status.mined ? 'Mined ✓' : 'Mine')}
          </button>
        </div>

        {/* Index Step */}
        <div className="border border-border rounded p-5 bg-panel shadow-sm flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-lg text-text">2. Index Embeddings</h3>
            <p className="text-sm text-muted">Vectorize sections for semantic similarity search.</p>
          </div>
          <button 
            onClick={handleIndex}
            disabled={loading !== '' || status.indexed}
            className="bg-accent/20 text-accent px-4 py-2 rounded hover:bg-accent/30 font-medium disabled:opacity-50 min-w-[120px]"
          >
            {loading === 'indexing' ? 'Working...' : (status.indexed ? 'Indexed ✓' : 'Index')}
          </button>
        </div>

        {/* Report Step */}
        <div className="border border-border rounded p-5 bg-panel shadow-sm flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-lg text-text">3. Generate LLM Report</h3>
            <p className="text-sm text-muted">Synthesize evidence into a comprehensive markdown report (requires Groq).</p>
          </div>
          <button 
            onClick={handleReport}
            disabled={loading !== ''}
            className="bg-accent text-text px-5 py-2 rounded hover:bg-accent/90 font-medium disabled:opacity-50 min-w-[120px]"
          >
            {loading === 'reporting' ? 'Generating...' : 'Run Report'}
          </button>
        </div>
      </div>
    </div>
  );
}
