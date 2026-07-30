from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.project import ProjectResponse, ProjectCreate, ProjectUpdate, ProjectStatus
from app.services.project_service import ProjectService
from app.api.deps import get_current_user_dep
from app.models.user import User

router = APIRouter()

def get_project_service(db: Session = Depends(get_db)) -> ProjectService:
    return ProjectService(db)

@router.get("", response_model=List[ProjectResponse])
def get_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search projects by name or description"),
    sort_by: Optional[str] = Query("updated_at", description="Field to sort by"),
    sort_desc: bool = Query(True, description="Sort descending"),
    status: Optional[ProjectStatus] = Query(None, description="Filter by status"),
    favorite: Optional[bool] = Query(None, description="Filter by favorite"),
    service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user_dep)
):
    return service.get_projects(
        current_user=current_user,
        skip=skip,
        limit=limit,
        search=search,
        sort_by=sort_by,
        sort_desc=sort_desc,
        status=status,
        favorite=favorite
    )

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: UUID = Path(...),
    service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user_dep)
):
    return service.get_project(project_id, current_user)

@router.post("", response_model=ProjectResponse, status_code=201)
def create_project(
    project_in: ProjectCreate,
    service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user_dep)
):
    return service.create_project(project_in, current_user)

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_in: ProjectUpdate,
    project_id: UUID = Path(...),
    service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user_dep)
):
    return service.update_project(project_id, project_in, current_user)
    
@router.patch("/{project_id}", response_model=ProjectResponse)
def patch_project(
    project_in: ProjectUpdate,
    project_id: UUID = Path(...),
    service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user_dep)
):
    # For now, patch does the same as put, since ProjectUpdate uses Optionals
    return service.update_project(project_id, project_in, current_user)

@router.delete("/{project_id}")
def delete_project(
    project_id: UUID = Path(...),
    service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user_dep)
):
    return service.delete_project(project_id, current_user)
    
@router.patch("/{project_id}/favorite", response_model=ProjectResponse)
def favorite_project(
    favorite: bool = Query(..., description="Set favorite status"),
    project_id: UUID = Path(...),
    service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user_dep)
):
    return service.favorite_project(project_id, favorite, current_user)
    
@router.patch("/{project_id}/archive", response_model=ProjectResponse)
def archive_project(
    project_id: UUID = Path(...),
    service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user_dep)
):
    return service.archive_project(project_id, current_user)
