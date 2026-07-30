import { Project } from '../types';
import { apiClient } from '@/api/client';

export const projectsApi = {
  getProjects: async (): Promise<Project[]> => {
    const data = await apiClient<any[]>('/api/v1/projects', { method: 'GET' });
    return data.map((d) => ({
      ...d,
      createdAt: d.created_at,
      updatedAt: d.updated_at,
      analysisCount: 0,
      lastAnalysis: null,
    }));
  },

  getProjectById: async (id: string): Promise<Project | null> => {
    try {
      const data = await apiClient<any>(`/api/v1/projects/${id}`, { method: 'GET' });
      return {
        ...data,
        createdAt: data.created_at,
        updatedAt: data.updated_at,
        analysisCount: 0,
        lastAnalysis: null,
      };
    } catch (err: any) {
      if (err.message?.includes('404')) {
        return null;
      }
      throw err;
    }
  },

  createProject: async (data: Omit<Project, 'id' | 'createdAt' | 'updatedAt' | 'analysisCount' | 'lastAnalysis'>): Promise<Project> => {
    const resData = await apiClient<any>('/api/v1/projects', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    return {
      ...resData,
      createdAt: resData.created_at,
      updatedAt: resData.updated_at,
      analysisCount: 0,
      lastAnalysis: null,
    };
  },

  updateProject: async (id: string, data: Partial<Project>): Promise<Project> => {
    const resData = await apiClient<any>(`/api/v1/projects/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
    return {
      ...resData,
      createdAt: resData.created_at,
      updatedAt: resData.updated_at,
      analysisCount: 0,
      lastAnalysis: null,
    };
  },

  deleteProject: async (id: string): Promise<void> => {
    await apiClient<void>(`/api/v1/projects/${id}`, { method: 'DELETE' });
  },
};
