import { PersistentAnalysis } from '../api/persistentAnalysis';
import { Link } from 'react-router-dom';
import { Trash2, Search, BarChart2, Hash, FileText } from 'lucide-react';

interface AnalysisHistoryCardProps {
  analysis: PersistentAnalysis;
  onDelete: () => void;
}

export function AnalysisHistoryCard({ analysis, onDelete }: AnalysisHistoryCardProps) {
  const getStatusBadge = () => {
    switch (analysis.status) {
      case 'completed':
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800 border border-emerald-200">Completed</span>;
      case 'failed':
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 border border-red-200">Failed</span>;
      case 'running':
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 border border-blue-200 animate-pulse">Running</span>;
      default:
        return <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 border border-gray-200">{analysis.status}</span>;
    }
  };

  return (
    <div className="bg-surface border border-border rounded-xl p-5 shadow-sm hover:border-blue-300 transition-colors flex flex-col md:flex-row gap-4 items-start md:items-center justify-between group">
      <div className="flex-1">
        <div className="flex items-center gap-3 mb-2">
          <Link to={`/analysis/${analysis.id}`} className="text-lg font-semibold text-text hover:text-primary transition-colors flex items-center">
            <Search className="w-4 h-4 mr-2 text-gray-400" />
            {analysis.query}
          </Link>
          {getStatusBadge()}
        </div>
        
        <div className="flex flex-wrap items-center gap-4 text-xs text-gray-500">
          <span className="flex items-center" title="Papers Indexed">
            <FileText className="w-3.5 h-3.5 mr-1" />
            {analysis.paper_count} Papers
          </span>
          <span className="flex items-center" title="Topics Discovered">
            <Hash className="w-3.5 h-3.5 mr-1" />
            {analysis.topic_count} Topics
          </span>
          <span className="flex items-center" title="Gaps Detected">
            <BarChart2 className="w-3.5 h-3.5 mr-1" />
            {analysis.gap_count} Gaps
          </span>
          <span className="text-gray-400">
            {new Date(analysis.created_at).toLocaleString()}
          </span>
        </div>
      </div>
      
      <div className="flex items-center gap-2">
        <Link 
          to={`/analysis/${analysis.id}`}
          className="px-4 py-2 bg-gray-50 hover:bg-gray-100 border border-gray-200 text-gray-700 text-sm font-medium rounded-lg transition-colors"
        >
          View Result
        </Link>
        <button 
          onClick={onDelete}
          className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
          title="Delete Analysis"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
