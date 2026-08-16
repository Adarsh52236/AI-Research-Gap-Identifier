import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import useAppStore from '../store/useAppStore';
import { searchPapers } from '../services/searchService';
import LoadingBall from '../components/common/LoadingBall';

export default function Home() {
  const [localQuery, setLocalQuery] = useState('');
  const [limit, setLimit] = useState(10);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const { setQuery, setResults, clearSelection } = useAppStore();
  const navigate = useNavigate();

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!localQuery.trim()) return;

    setLoading(true);
    setError(null);
    try {
      const data = await searchPapers(localQuery, limit);
      setQuery(localQuery);
      setResults(data.results || []);
      clearSelection();
      navigate('/results');
    } catch (err) {
      setError(err.message || 'Search failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto mt-20 p-6 bg-panel rounded-lg shadow-sm border border-border">
      <h1 className="text-3xl font-semibold mb-6 text-text">Discover Research Gaps</h1>
      <p className="text-muted mb-8">
        Search for papers to download, extract, and mine for insights.
      </p>
      
      {error && (
        <div className="mb-4 p-3 bg-red-900/20 border border-red-500/50 text-red-400 rounded">
          {error}
        </div>
      )}

      <form onSubmit={handleSearch} className="space-y-6">
        <div className="relative">
          <label className="block text-sm font-medium text-text mb-2">
            Research Query
          </label>
          <input
            type="text"
            className="w-full p-3 border border-border rounded focus:ring-2 focus:ring-accent focus:border-transparent focus:outline-none bg-bg text-text"
            placeholder="e.g. KV cache optimization for LLMs"
            value={localQuery}
            onChange={(e) => setLocalQuery(e.target.value)}
            disabled={loading}
          />
          {loading && (
            <div className="absolute right-4 -top-8 transform scale-75 pointer-events-none">
              <LoadingBall />
            </div>
          )}
        </div>
        
        <div>
          <label className="block text-sm font-medium text-text mb-2">
            Max Results
          </label>
          <input
            type="number"
            min="1"
            max="50"
            className="w-full p-3 border border-border rounded focus:ring-2 focus:ring-accent focus:border-transparent focus:outline-none bg-bg text-text"
            value={limit}
            onChange={(e) => setLimit(Number(e.target.value))}
            disabled={loading}
          />
        </div>

        <button
          type="submit"
          className="w-full bg-accent hover:bg-accent/90 text-text font-medium py-3 rounded transition disabled:opacity-50"
          disabled={loading || !localQuery.trim()}
        >
          {loading ? 'Searching...' : 'Search Papers'}
        </button>
      </form>
    </div>
  );
}
