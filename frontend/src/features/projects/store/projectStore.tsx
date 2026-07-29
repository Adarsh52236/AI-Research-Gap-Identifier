import { createContext, useContext, useState, ReactNode, useCallback } from 'react';
import { Project, ProjectStatus } from '../types';
import { projectsApi } from '../api/projects';

interface ProjectStoreContextType {
  projects: Project[];
  isLoading: boolean;
  error: string | null;
  fetchProjects: () => Promise<void>;
  createProject: (data: Omit<Project, 'id' | 'createdAt' | 'updatedAt' | 'analysisCount' | 'lastAnalysis'>) => Promise<void>;
  updateProject: (id: string, data: Partial<Project>) => Promise<void>;
  deleteProject: (id: string) => Promise<void>;
  
  // Selectors mapped as getters/functions
  getProject: (id: string) => Project | undefined;
  activeProjects: () => Project[];
  favoriteProjects: () => Project[];
}

const ProjectStoreContext = createContext<ProjectStoreContextType | undefined>(undefined);

export function ProjectStoreProvider({ children }: { children: ReactNode }) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchProjects = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await projectsApi.getProjects();
      setProjects(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch projects');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const createProject = useCallback(async (data: Omit<Project, 'id' | 'createdAt' | 'updatedAt' | 'analysisCount' | 'lastAnalysis'>) => {
    try {
      const newProject = await projectsApi.createProject(data);
      setProjects(prev => [newProject, ...prev]);
    } catch (err: any) {
      throw new Error(err.message || 'Failed to create project');
    }
  }, []);

  const updateProject = useCallback(async (id: string, data: Partial<Project>) => {
    try {
      const updatedProject = await projectsApi.updateProject(id, data);
      setProjects(prev => prev.map(p => p.id === id ? updatedProject : p));
    } catch (err: any) {
      throw new Error(err.message || 'Failed to update project');
    }
  }, []);

  const deleteProject = useCallback(async (id: string) => {
    try {
      await projectsApi.deleteProject(id);
      setProjects(prev => prev.filter(p => p.id !== id));
    } catch (err: any) {
      throw new Error(err.message || 'Failed to delete project');
    }
  }, []);

  const getProject = useCallback((id: string) => {
    return projects.find(p => p.id === id);
  }, [projects]);

  const activeProjects = useCallback(() => {
    return projects.filter(p => p.status === ProjectStatus.ACTIVE);
  }, [projects]);

  const favoriteProjects = useCallback(() => {
    return projects.filter(p => p.favorite);
  }, [projects]);

  return (
    <ProjectStoreContext.Provider 
      value={{ 
        projects, 
        isLoading, 
        error, 
        fetchProjects, 
        createProject, 
        updateProject, 
        deleteProject,
        getProject,
        activeProjects,
        favoriteProjects
      }}
    >
      {children}
    </ProjectStoreContext.Provider>
  );
}

export function useProjectStore() {
  const context = useContext(ProjectStoreContext);
  if (context === undefined) {
    throw new Error('useProjectStore must be used within a ProjectStoreProvider');
  }
  return context;
}
