import { PageContainer } from '@/components/layout/PageContainer';
import { useProjectStore } from '../store/projectStore';
import { useProjectSearch } from '../hooks/useProjectSearch';
import { useProjectSort } from '../hooks/useProjectSort';
import { ProjectGrid } from '../components/ProjectGrid';
import { ProjectEmptyState } from '../components/ProjectEmptyState';
import { CreateProjectDialog } from '../components/CreateProjectDialog';
import { ProjectGridSkeleton } from '../components/ProjectGridSkeleton';
import { useState, useEffect } from 'react';
import { Search, FolderPlus, SlidersHorizontal } from 'lucide-react';
import { ProjectSortOption } from '../types';

export function ProjectsPage() {
  const { projects, isLoading, fetchProjects } = useProjectStore();
  const [isCreateOpen, setIsCreateOpen] = useState(false);

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  const { searchQuery, setSearchQuery, filteredProjects } = useProjectSearch(projects);
  const { sortOption, setSortOption, sortedProjects } = useProjectSort(filteredProjects);

  const isEmpty = projects.length === 0 && !isLoading;
  const hasNoSearchResults = projects.length > 0 && sortedProjects.length === 0;

  return (
    <PageContainer>
      <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
        <div>
          <h1 className="text-3xl font-bold text-text">Research Projects</h1>
          <p className="text-muted mt-1">Manage and organize your AI literature analysis workspaces.</p>
        </div>
        
        {!isEmpty && !isLoading && (
          <button
            onClick={() => setIsCreateOpen(true)}
            className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
          >
            <FolderPlus className="w-5 h-5 mr-2" />
            New Project
          </button>
        )}
      </div>

      {!isEmpty && !isLoading && (
        <div className="flex flex-col md:flex-row gap-4 mb-6">
          <div className="relative flex-1 max-w-lg">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              className="block w-full pl-10 pr-3 py-2 border border-border rounded-md leading-5 bg-surface text-text placeholder-gray-500 focus:outline-none focus:bg-white focus:ring-2 focus:ring-primary focus:border-primary sm:text-sm"
              placeholder="Search projects by name, description, or tags..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          
          <div className="relative flex items-center">
            <SlidersHorizontal className="h-4 w-4 text-gray-400 mr-2" />
            <select
              value={sortOption}
              onChange={(e) => setSortOption(e.target.value as ProjectSortOption)}
              className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm rounded-md bg-surface border"
            >
              <option value="recently_updated">Recently Updated</option>
              <option value="recently_created">Recently Created</option>
              <option value="alphabetical">Alphabetical</option>
            </select>
          </div>
        </div>
      )}

      {isLoading && (
        <ProjectGridSkeleton />
      )}

      {!isLoading && isEmpty && (
        <ProjectEmptyState onCreateClick={() => setIsCreateOpen(true)} />
      )}

      {!isLoading && hasNoSearchResults && (
        <div className="text-center py-12 bg-surface rounded-xl border border-border">
          <p className="text-muted">No projects found matching "{searchQuery}"</p>
          <button 
            onClick={() => setSearchQuery('')}
            className="mt-4 text-primary hover:underline font-medium"
          >
            Clear search
          </button>
        </div>
      )}

      {!isLoading && sortedProjects.length > 0 && (
        <ProjectGrid projects={sortedProjects} />
      )}

      <CreateProjectDialog isOpen={isCreateOpen} onClose={() => setIsCreateOpen(false)} />
    </PageContainer>
  );
}
