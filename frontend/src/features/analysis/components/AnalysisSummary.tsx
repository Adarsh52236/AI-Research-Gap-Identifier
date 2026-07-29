import { AnalysisResponse } from '../types';
import { Clock, BookOpen, Layers, Lightbulb } from 'lucide-react';
import { CopyButton } from '@/components/ui/CopyButton';

interface AnalysisSummaryProps {
  data: AnalysisResponse;
}

export function AnalysisSummary({ data }: AnalysisSummaryProps) {
  const stats = [
    { label: 'Papers Analyzed', value: data.papers_indexed, icon: BookOpen, color: 'text-blue-500' },
    { label: 'Topics Discovered', value: data.topics.topics.length, icon: Layers, color: 'text-indigo-500' },
    { label: 'Gaps Identified', value: data.gaps.total_gaps, icon: Lightbulb, color: 'text-amber-500' },
    { label: 'Processing Time', value: `${data.duration_seconds.toFixed(1)}s`, icon: Clock, color: 'text-emerald-500' },
  ];

  const summaryText = `Executive Summary for "${data.query}":\nAnalyzed ${data.papers_indexed} papers in ${data.duration_seconds.toFixed(1)}s.\nDiscovered ${data.topics.topics.length} topics and ${data.gaps.total_gaps} research gaps.`;

  return (
    <div className="bg-surface rounded-xl shadow-sm border border-border p-6 mb-8">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold text-text">Executive Summary</h2>
        <CopyButton text={summaryText} label="Copy Stats" />
      </div>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, idx) => {
          const Icon = stat.icon;
          return (
            <div key={idx} className="bg-background rounded-lg p-4 border border-border flex items-center">
              <div className={`p-3 rounded-full bg-white shadow-sm mr-4 ${stat.color}`}>
                <Icon className="w-6 h-6" />
              </div>
              <div>
                <p className="text-sm text-muted font-medium">{stat.label}</p>
                <p className="text-2xl font-bold text-text">{stat.value}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
