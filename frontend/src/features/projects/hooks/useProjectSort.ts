import { useState, useMemo } from 'react';
import { Project, ProjectSortOption } from '../types';

export function useProjectSort(projects: Project[], defaultSort: ProjectSortOption = 'recently_updated') {
  const [sortOption, setSortOption] = useState<ProjectSortOption>(defaultSort);

  const sortedProjects = useMemo(() => {
    const projectsCopy = [...projects];
    
    return projectsCopy.sort((a, b) => {
      switch (sortOption) {
        case 'recently_updated':
          return new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime();
        case 'recently_created':
          return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
        case 'alphabetical':
          return a.name.localeCompare(b.name);
        default:
          return 0;
      }
    });
  }, [projects, sortOption]);

  return {
    sortOption,
    setSortOption,
    sortedProjects,
  };
}
