import { Project } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1';
const PROJECTS_URL = `${API_BASE_URL.replace('/api/v1', '')}/projects`;

export const projectsApi = {
  getProjects: async (): Promise<Project[]> => {
    const response = await fetch(PROJECTS_URL);
    if (!response.ok) throw new Error('Failed to fetch projects');
    const data = await response.json();
    return data.map((d: any) => ({
      ...d,
      createdAt: d.created_at,
      updatedAt: d.updated_at,
      analysisCount: 0, // Placeholder mapping since backend doesn't track this yet
      lastAnalysis: null,
    }));
  },

  getProjectById: async (id: string): Promise<Project | null> => {
    const response = await fetch(`${PROJECTS_URL}/${id}`);
    if (response.status === 404) return null;
    if (!response.ok) throw new Error('Failed to fetch project');
    const data = await response.json();
    return {
      ...data,
      createdAt: data.created_at,
      updatedAt: data.updated_at,
      analysisCount: 0,
      lastAnalysis: null,
    };
  },

  createProject: async (data: Omit<Project, 'id' | 'createdAt' | 'updatedAt' | 'analysisCount' | 'lastAnalysis'>): Promise<Project> => {
    const response = await fetch(PROJECTS_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to create project');
    }
    const resData = await response.json();
    return {
      ...resData,
      createdAt: resData.created_at,
      updatedAt: resData.updated_at,
      analysisCount: 0,
      lastAnalysis: null,
    };
  },

  updateProject: async (id: string, data: Partial<Project>): Promise<Project> => {
    const response = await fetch(`${PROJECTS_URL}/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to update project');
    }
    const resData = await response.json();
    return {
      ...resData,
      createdAt: resData.created_at,
      updatedAt: resData.updated_at,
      analysisCount: 0,
      lastAnalysis: null,
    };
  },

  deleteProject: async (id: string): Promise<void> => {
    const response = await fetch(`${PROJECTS_URL}/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to delete project');
  },
};
