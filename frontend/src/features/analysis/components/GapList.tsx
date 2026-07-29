import { ResearchGap } from '../types';
import { Target, Activity, FileText } from 'lucide-react';

interface GapListProps {
  gaps: ResearchGap[];
}

export function GapList({ gaps }: GapListProps) {
  if (!gaps.length) return null;

  return (
    <div className="bg-surface rounded-xl shadow-sm border border-border p-6 mb-8">
      <h2 className="text-lg font-semibold text-text mb-4">Identified Research Gaps</h2>
      
      <div className="space-y-4">
        {gaps.map((gap) => (
          <div key={gap.id} className="border border-border rounded-lg p-5 bg-background hover:border-primary/50 transition-colors">
            <div className="flex justify-between items-start mb-3">
              <h3 className="text-lg font-bold text-text">{gap.title}</h3>
              <div className="flex items-center bg-emerald-50 text-emerald-700 px-3 py-1 rounded-full text-sm font-bold border border-emerald-200">
                <Target className="w-4 h-4 mr-1.5" />
                {(gap.confidence * 100).toFixed(0)}% Confidence
              </div>
            </div>
            
            <p className="text-muted mb-4">{gap.description}</p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t border-border">
              <div>
                <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2 flex items-center">
                  <Activity className="w-3 h-3 mr-1" /> Strategy Engine
                </h4>
                <span className="inline-block bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded font-medium">
                  {gap.strategy}
                </span>
              </div>
              
              <div>
                <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2 flex items-center">
                  <FileText className="w-3 h-3 mr-1" /> Supporting Evidence
                </h4>
                <ul className="text-sm text-muted space-y-1">
                  {gap.evidence.slice(0, 2).map((ev, i) => (
                    <li key={i} className="flex items-start">
                      <span className="text-primary mr-2">•</span>
                      <span className="line-clamp-2">{ev.message}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
