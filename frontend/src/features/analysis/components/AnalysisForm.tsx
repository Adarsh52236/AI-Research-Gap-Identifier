import { useState } from 'react';
import { Search, BrainCircuit, Library, Lightbulb } from 'lucide-react';
import { EXAMPLE_TOPICS } from '../constants/exampleTopics';

interface AnalysisFormProps {
  onSubmit: (query: string, maxResults: number) => void;
  isLoading: boolean;
}

export function AnalysisForm({ onSubmit, isLoading }: AnalysisFormProps) {
  const [query, setQuery] = useState('');
  const [maxResults, setMaxResults] = useState(100);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    onSubmit(query.trim(), maxResults);
  };

  return (
    <div className="space-y-8">
      <div className="bg-surface rounded-xl shadow-sm border border-border overflow-hidden">
        <div className="bg-gradient-to-r from-blue-600 to-indigo-700 px-8 py-12 text-white">
          <h1 className="text-3xl font-bold mb-3 tracking-tight">Research Analysis</h1>
          <p className="text-blue-100 text-lg max-w-2xl">
            Discover research topics, identify trends, and uncover research gaps using AI.
          </p>
        </div>
        
        <form onSubmit={handleSubmit} className="p-8">
          <div className="space-y-4 mb-6">
            <div>
              <label htmlFor="query" className="block text-sm font-medium text-text mb-1">
                Research Topic
              </label>
              <input
                id="query"
                type="text"
                required
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="e.g. Transformers in medical imaging"
                className="w-full px-4 py-3 border border-border rounded-md focus:ring-2 focus:ring-primary focus:border-primary outline-none text-text bg-background text-lg"
                disabled={isLoading}
              />
            </div>
            
            <div>
              <label htmlFor="maxResults" className="block text-sm font-medium text-text mb-1">
                Maximum Papers to Analyze
              </label>
              <input
                id="maxResults"
                type="number"
                min={10}
                max={500}
                value={maxResults}
                onChange={(e) => setMaxResults(Number(e.target.value))}
                className="w-full md:w-48 px-4 py-2 border border-border rounded-md focus:ring-2 focus:ring-primary focus:border-primary outline-none text-text bg-background"
                disabled={isLoading}
              />
            </div>
          </div>

          <div className="mb-6">
            <p className="text-sm text-muted mb-2 font-medium">Or try an example topic:</p>
            <div className="flex flex-wrap gap-2">
              {EXAMPLE_TOPICS.map((topic, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => setQuery(topic)}
                  className="px-3 py-1.5 text-sm bg-blue-50 text-blue-700 rounded-full hover:bg-blue-100 transition-colors border border-blue-200"
                >
                  {topic}
                </button>
              ))}
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading || !query.trim()}
            className="flex items-center justify-center px-8 py-3 w-full md:w-auto border border-transparent text-base font-bold rounded-md text-white bg-primary hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-sm"
          >
            <Search className="w-5 h-5 mr-2" />
            {isLoading ? 'Initializing Analysis...' : 'Analyze Research'}
          </button>
        </form>
      </div>

      {/* 3-step workflow illustration */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-surface border border-border rounded-xl p-6 text-center shadow-sm">
          <div className="w-12 h-12 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <Library className="w-6 h-6" />
          </div>
          <h3 className="font-bold text-text mb-2">1. Aggregate</h3>
          <p className="text-sm text-muted">Fetches and indexes hundreds of scholarly papers from the latest databases.</p>
        </div>

        <div className="bg-surface border border-border rounded-xl p-6 text-center shadow-sm">
          <div className="w-12 h-12 bg-indigo-100 text-indigo-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <BrainCircuit className="w-6 h-6" />
          </div>
          <h3 className="font-bold text-text mb-2">2. Model</h3>
          <p className="text-sm text-muted">Generates dense vector embeddings and clusters them into distinct research topics.</p>
        </div>

        <div className="bg-surface border border-border rounded-xl p-6 text-center shadow-sm">
          <div className="w-12 h-12 bg-amber-100 text-amber-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <Lightbulb className="w-6 h-6" />
          </div>
          <h3 className="font-bold text-text mb-2">3. Synthesize</h3>
          <p className="text-sm text-muted">Uses Large Language Models to identify gaps and generate actionable insights.</p>
        </div>
      </div>
    </div>
  );
}
