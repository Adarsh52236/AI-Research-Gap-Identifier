import { useAnalysisStore } from '@/store/analysisStore';
import { Clock, CheckCircle2, XCircle } from 'lucide-react';

interface AnalysisHistoryProps {
  onSelect: (id: string) => void;
  activeId?: string | null;
}

export function AnalysisHistory({ onSelect, activeId }: AnalysisHistoryProps) {
  const { sessions } = useAnalysisStore();

  if (sessions.length === 0) return null;

  return (
    <div className="bg-surface rounded-xl shadow-sm border border-border p-4 mb-6">
      <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">
        Session History
      </h3>
      <div className="space-y-2 max-h-60 overflow-y-auto pr-2">
        {sessions.map((session) => (
          <button
            key={session.id}
            onClick={() => onSelect(session.id)}
            className={`w-full flex flex-col p-3 rounded-lg border text-left transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-1 ${
              activeId === session.id
                ? 'bg-blue-50 border-blue-200'
                : 'bg-background border-border hover:border-blue-300'
            }`}
          >
            <div className="flex items-center justify-between mb-1">
              <span className="font-medium text-text truncate pr-2 max-w-[200px]">
                {session.query}
              </span>
              {session.status === 'success' ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-500 flex-shrink-0" />
              ) : (
                <XCircle className="w-4 h-4 text-red-500 flex-shrink-0" />
              )}
            </div>
            <div className="flex items-center text-xs text-muted">
              <Clock className="w-3 h-3 mr-1" />
              {new Date(session.timestamp).toLocaleTimeString()}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
