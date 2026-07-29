import { AnalysisSession } from '../types';
import { Download, FileText, FileJson } from 'lucide-react';
import { useState } from 'react';

interface AnalysisHeaderProps {
  session: AnalysisSession;
}

export function AnalysisHeader({ session }: AnalysisHeaderProps) {
  const [exportOpen, setExportOpen] = useState(false);

  const handleExportJSON = () => {
    if (!session.data) return;
    const blob = new Blob([JSON.stringify(session.data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `researchos-analysis-${session.timestamp}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    setExportOpen(false);
  };

  if (!session.data) return null;

  return (
    <div className="flex flex-col md:flex-row justify-between items-start md:items-center bg-surface border border-border rounded-xl p-6 mb-6 shadow-sm relative">
      <div>
        <h1 className="text-2xl font-bold text-text mb-1">Analysis: "{session.query}"</h1>
        <div className="flex items-center gap-4 text-sm text-muted">
          <span className="flex items-center">
            <span className="w-2 h-2 rounded-full bg-emerald-500 mr-2"></span>
            Completed
          </span>
          <span>•</span>
          <span>{session.metadata?.durationSeconds.toFixed(1)}s elapsed</span>
          <span>•</span>
          <span>{new Date(session.timestamp).toLocaleString()}</span>
        </div>
      </div>

      <div className="mt-4 md:mt-0 relative">
        <button 
          onClick={() => setExportOpen(!exportOpen)}
          className="inline-flex items-center justify-center px-4 py-2 border border-border rounded-md shadow-sm text-sm font-medium text-text bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
        >
          <Download className="w-4 h-4 mr-2" />
          Export
        </button>

        {exportOpen && (
          <div className="absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-20">
            <div className="py-1" role="menu" aria-orientation="vertical">
              <button
                onClick={handleExportJSON}
                className="w-full text-left flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 hover:text-gray-900"
                role="menuitem"
              >
                <FileJson className="w-4 h-4 mr-2 text-gray-400" />
                Raw JSON
              </button>
              <button
                disabled
                className="w-full text-left flex items-center px-4 py-2 text-sm text-gray-400 cursor-not-allowed"
                role="menuitem"
              >
                <FileText className="w-4 h-4 mr-2 text-gray-300" />
                PDF Report (Coming Soon)
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
