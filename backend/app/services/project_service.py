from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectStatus
from app.repositories.project_repository import ProjectRepository

class ProjectService:
    def __init__(self, db: Session):
        self.repository = ProjectRepository(db)

    def get_projects(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        search: Optional[str] = None,
        sort_by: Optional[str] = "updated_at",
        sort_desc: bool = True,
        status: Optional[ProjectStatus] = None,
        favorite: Optional[bool] = None
    ) -> List[Project]:
        return self.repository.get_all(skip, limit, search, sort_by, sort_desc, status, favorite)

    def get_project(self, project_id: UUID) -> Project:
        project = self.repository.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project

    def create_project(self, project_in: ProjectCreate) -> Project:
        existing = self.repository.get_by_name(project_in.name)
        if existing:
            raise HTTPException(status_code=409, detail="Project with this name already exists")
        return self.repository.create(project_in)

    def update_project(self, project_id: UUID, project_in: ProjectUpdate) -> Project:
        project = self.get_project(project_id)
        
        if project_in.name and project_in.name != project.name:
            existing = self.repository.get_by_name(project_in.name)
            if existing:
                raise HTTPException(status_code=409, detail="Project with this name already exists")
                
        return self.repository.update(project, project_in)

    def delete_project(self, project_id: UUID) -> dict:
        project = self.get_project(project_id)
        self.repository.delete(project)
        return {"message": "Project deleted successfully"}
        
    def favorite_project(self, project_id: UUID, favorite: bool) -> Project:
        project = self.get_project(project_id)
        return self.repository.favorite(project, favorite)
        
    def archive_project(self, project_id: UUID) -> Project:
        project = self.get_project(project_id)
        return self.repository.archive(project)
