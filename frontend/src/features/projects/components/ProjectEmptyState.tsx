import { FolderPlus } from 'lucide-react';

interface ProjectEmptyStateProps {
  onCreateClick: () => void;
}

export function ProjectEmptyState({ onCreateClick }: ProjectEmptyStateProps) {
  return (
    <div className="text-center py-20 bg-surface rounded-xl border border-dashed border-gray-300">
      <div className="mx-auto w-16 h-16 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center mb-4">
        <FolderPlus className="w-8 h-8" />
      </div>
      <h3 className="text-xl font-semibold text-text mb-2">No projects yet</h3>
      <p className="text-muted max-w-md mx-auto mb-6">
        Create your first research project to organize your analyses, store AI insights, and track research gaps over time.
      </p>
      <button
        onClick={onCreateClick}
        className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
      >
        <FolderPlus className="w-5 h-5 mr-2" />
        Create Project
      </button>
    </div>
  );
}
