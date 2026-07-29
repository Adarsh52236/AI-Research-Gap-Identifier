import { TopicInfo } from '../types';

interface TopicListProps {
  topics: TopicInfo[];
}

export function TopicList({ topics }: TopicListProps) {
  if (!topics.length) return null;

  return (
    <div className="bg-surface rounded-xl shadow-sm border border-border p-6 mb-8">
      <h2 className="text-lg font-semibold text-text mb-4">Discovered Topics</h2>
      <div className="flex flex-wrap gap-2">
        {topics.map((topic) => (
          <div 
            key={topic.id} 
            className="inline-flex items-center px-3 py-1 rounded-full bg-blue-50 text-blue-700 border border-blue-200 text-sm font-medium"
          >
            <span className="mr-2 truncate max-w-[200px]">{topic.name}</span>
            <span className="bg-blue-100 text-blue-800 text-xs py-0.5 px-2 rounded-full">
              {topic.document_count} papers
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
