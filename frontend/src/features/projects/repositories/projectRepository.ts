import { Project } from '../types';

class ProjectRepository {
  private projects: Map<string, Project> = new Map();

  constructor() {
    // Seed with a dummy project for testing empty vs non-empty states if desired,
    // but the requirement implies starting empty.
  }

  async getAll(): Promise<Project[]> {
    return Array.from(this.projects.values());
  }

  async getById(id: string): Promise<Project | null> {
    return this.projects.get(id) || null;
  }

  async create(data: Omit<Project, 'id' | 'createdAt' | 'updatedAt' | 'analysisCount' | 'lastAnalysis'>): Promise<Project> {
    const id = crypto.randomUUID();
    const now = new Date().toISOString();
    
    const project: Project = {
      ...data,
      id,
      createdAt: now,
      updatedAt: now,
      analysisCount: 0,
      lastAnalysis: null,
    };
    
    this.projects.set(id, project);
    return project;
  }

  async update(id: string, data: Partial<Project>): Promise<Project> {
    const existing = await this.getById(id);
    if (!existing) {
      throw new Error(`Project with id ${id} not found`);
    }

    const updated: Project = {
      ...existing,
      ...data,
      updatedAt: new Date().toISOString(),
    };

    this.projects.set(id, updated);
    return updated;
  }

  async delete(id: string): Promise<void> {
    if (!this.projects.has(id)) {
      throw new Error(`Project with id ${id} not found`);
    }
    this.projects.delete(id);
  }
}

export const projectRepository = new ProjectRepository();
