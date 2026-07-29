export enum ProjectStatus {
  ACTIVE = 'active',
  ARCHIVED = 'archived',
  COMPLETED = 'completed'
}

export interface Project {
  id: string;
  name: string;
  description: string;
  createdAt: string;
  updatedAt: string;
  analysisCount: number;
  lastAnalysis: string | null;
  status: ProjectStatus;
  tags: string[];
  favorite: boolean;
}

export type ProjectSortOption = 'recently_updated' | 'recently_created' | 'alphabetical';
