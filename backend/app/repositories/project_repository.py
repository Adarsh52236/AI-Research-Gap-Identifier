from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_, desc, asc

from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectStatus

class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_owned_project(self, project_id: UUID, user_id: UUID) -> Optional[Project]:
        stmt = select(Project).where(
            and_(
                Project.id == project_id, 
                Project.user_id == user_id,
                Project.deleted_at.is_(None)
            )
        )
        return self.db.execute(stmt).scalar_one_or_none()
        
    def get_owned_project_by_name(self, name: str, user_id: UUID) -> Optional[Project]:
        stmt = select(Project).where(
            and_(
                Project.name == name, 
                Project.user_id == user_id,
                Project.deleted_at.is_(None)
            )
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def list_owned_projects(
        self, 
        user_id: UUID,
        skip: int = 0, 
        limit: int = 100, 
        search: Optional[str] = None,
        sort_by: Optional[str] = "updated_at",
        sort_desc: bool = True,
        status: Optional[ProjectStatus] = None,
        favorite: Optional[bool] = None
    ) -> List[Project]:
        stmt = select(Project).where(
            and_(
                Project.user_id == user_id,
                Project.deleted_at.is_(None)
            )
        )

        if search:
            search_term = f"%{search}%"
            stmt = stmt.where(
                or_(
                    Project.name.ilike(search_term),
                    Project.description.ilike(search_term)
                )
            )
            
        if status:
            stmt = stmt.where(Project.status == status)
            
        if favorite is not None:
            stmt = stmt.where(Project.favorite == favorite)

        if sort_by:
            column = getattr(Project, sort_by, Project.updated_at)
            stmt = stmt.order_by(desc(column) if sort_desc else asc(column))

        stmt = stmt.offset(skip).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def create(self, project_in: ProjectCreate, user_id: UUID) -> Project:
        db_obj = Project(
            name=project_in.name,
            description=project_in.description,
            status=project_in.status,
            tags=project_in.tags,
            user_id=user_id
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, db_obj: Project, project_in: ProjectUpdate) -> Project:
        update_data = project_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, db_obj: Project) -> Project:
        from datetime import datetime, timezone
        db_obj.deleted_at = datetime.now(timezone.utc)
        self.db.commit()
        return db_obj
        
    def favorite(self, db_obj: Project, favorite: bool) -> Project:
        db_obj.favorite = favorite
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
        
    def archive(self, db_obj: Project) -> Project:
        db_obj.status = ProjectStatus.ARCHIVED
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
