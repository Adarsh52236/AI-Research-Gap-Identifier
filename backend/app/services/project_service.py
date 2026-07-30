from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectStatus
from app.repositories.project_repository import ProjectRepository

class ProjectService:
    def __init__(self, db: Session):
        self.repository = ProjectRepository(db)

    def get_projects(
        self,
        current_user: User,
        skip: int = 0, 
        limit: int = 100, 
        search: Optional[str] = None,
        sort_by: Optional[str] = "updated_at",
        sort_desc: bool = True,
        status: Optional[ProjectStatus] = None,
        favorite: Optional[bool] = None
    ) -> List[Project]:
        return self.repository.list_owned_projects(
            user_id=current_user.id,
            skip=skip, limit=limit, search=search,
            sort_by=sort_by, sort_desc=sort_desc,
            status=status, favorite=favorite
        )

    def get_project(self, project_id: UUID, current_user: User) -> Project:
        project = self.repository.get_owned_project(project_id, current_user.id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project

    def create_project(self, project_in: ProjectCreate, current_user: User) -> Project:
        existing = self.repository.get_owned_project_by_name(project_in.name, current_user.id)
        if existing:
            raise HTTPException(status_code=409, detail="Project with this name already exists")
        return self.repository.create(project_in, current_user.id)

    def update_project(self, project_id: UUID, project_in: ProjectUpdate, current_user: User) -> Project:
        project = self.get_project(project_id, current_user)
        
        if project_in.name and project_in.name != project.name:
            existing = self.repository.get_owned_project_by_name(project_in.name, current_user.id)
            if existing:
                raise HTTPException(status_code=409, detail="Project with this name already exists")
                
        return self.repository.update(project, project_in)

    def delete_project(self, project_id: UUID, current_user: User) -> dict:
        project = self.get_project(project_id, current_user)
        self.repository.delete(project)
        return {"message": "Project deleted successfully"}
        
    def favorite_project(self, project_id: UUID, favorite: bool, current_user: User) -> Project:
        project = self.get_project(project_id, current_user)
        return self.repository.favorite(project, favorite)
        
    def archive_project(self, project_id: UUID, current_user: User) -> Project:
        project = self.get_project(project_id, current_user)
        return self.repository.archive(project)
