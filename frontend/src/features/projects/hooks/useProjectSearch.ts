import { useState, useMemo } from 'react';
import { Project } from '../types';

export function useProjectSearch(projects: Project[]) {
  const [searchQuery, setSearchQuery] = useState('');

  const filteredProjects = useMemo(() => {
    if (!searchQuery.trim()) return projects;
    
    const query = searchQuery.toLowerCase();
    return projects.filter(project => 
      project.name.toLowerCase().includes(query) || 
      project.description.toLowerCase().includes(query) ||
      project.tags.some(tag => tag.toLowerCase().includes(query))
    );
  }, [projects, searchQuery]);

  return {
    searchQuery,
    setSearchQuery,
    filteredProjects,
  };
}
