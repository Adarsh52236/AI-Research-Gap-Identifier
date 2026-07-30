from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from app.models.analysis import Analysis
from app.schemas.analysis import AnalysisCreate, AnalysisUpdate
from app.core.enums import AnalysisStatus

class AnalysisRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, analysis_in: AnalysisCreate) -> Analysis:
        db_obj = Analysis(
            project_id=analysis_in.project_id,
            query=analysis_in.query,
            status=AnalysisStatus.RUNNING,
            started_at=datetime.now(timezone.utc)
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def get_owned_analysis(self, analysis_id: UUID, user_id: UUID) -> Optional[Analysis]:
        from app.models.project import Project
        stmt = select(Analysis).join(Project).where(
            and_(
                Analysis.id == analysis_id,
                Project.user_id == user_id,
                Analysis.deleted_at.is_(None),
                Project.deleted_at.is_(None)
            )
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def list_project_analyses(self, project_id: UUID, user_id: UUID) -> List[Analysis]:
        from app.models.project import Project
        stmt = select(Analysis).join(Project).where(
            and_(
                Analysis.project_id == project_id,
                Project.user_id == user_id,
                Analysis.deleted_at.is_(None),
                Project.deleted_at.is_(None)
            )
        )
        return list(self.db.execute(stmt).scalars().all())

    def update(self, db_obj: Analysis, analysis_in: AnalysisUpdate) -> Analysis:
        update_data = analysis_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def soft_delete(self, db_obj: Analysis) -> Analysis:
        db_obj.deleted_at = datetime.now(timezone.utc)
        self.db.commit()
        return db_obj
