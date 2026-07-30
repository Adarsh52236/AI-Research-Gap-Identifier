from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Query, Path, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.analysis import AnalysisResponse, AnalysisCreate, AnalysisListItem
from app.services.analysis_service import AnalysisService
from app.services.project_service import ProjectService
from app.services.research_analysis.service import ResearchAnalysisService
from app.api.endpoints.analysis import get_research_analysis_service
from app.services.research_analysis.exceptions import ResearchAnalysisError
from app.api.deps import get_current_user_dep
from app.models.user import User

router = APIRouter()

def get_persistence_analysis_service(
    db: Session = Depends(get_db),
    ai_service: ResearchAnalysisService = Depends(get_research_analysis_service)
) -> AnalysisService:
    return AnalysisService(db, ai_service)

def get_project_service(db: Session = Depends(get_db)) -> ProjectService:
    return ProjectService(db)

@router.post("/projects/{project_id}/analyses", response_model=AnalysisResponse, status_code=201)
def create_analysis(
    project_id: UUID = Path(...),
    query: str = Query(..., description="The research query to analyze"),
    max_results: int = Query(100, description="Max papers to fetch"),
    service: AnalysisService = Depends(get_persistence_analysis_service),
    project_svc: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user_dep)
):
    # Verify project exists and is owned by current_user (will raise 404 if not found/owned)
    project_svc.get_project(project_id, current_user)
    
    try:
        return service.run_analysis_for_project(project_id, query, current_user, max_results)
    except ResearchAnalysisError as e:
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected pipeline failure")

@router.get("/projects/{project_id}/analyses", response_model=List[AnalysisListItem])
def list_analyses(
    project_id: UUID = Path(...),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort: str = Query("created_at", description="Field to sort by"),
    service: AnalysisService = Depends(get_persistence_analysis_service),
    project_svc: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user_dep)
):
    # Verify project exists and is owned by current_user
    project_svc.get_project(project_id, current_user)
    
    # Delegate to service
    analyses = service.list_project_analyses(project_id, current_user)
    
    # Sort
    reverse = sort.startswith("-")
    sort_key = sort.lstrip("-")
    analyses = sorted(analyses, key=lambda x: getattr(x, sort_key, getattr(x, "created_at")), reverse=reverse)
    
    # Paginate
    start = (page - 1) * page_size
    end = start + page_size
    return analyses[start:end]

@router.get("/analyses/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(
    analysis_id: UUID = Path(...),
    service: AnalysisService = Depends(get_persistence_analysis_service),
    current_user: User = Depends(get_current_user_dep)
):
    return service.get_analysis(analysis_id, current_user)

@router.delete("/analyses/{analysis_id}", status_code=204)
def delete_analysis(
    analysis_id: UUID = Path(...),
    service: AnalysisService = Depends(get_persistence_analysis_service),
    current_user: User = Depends(get_current_user_dep)
):
    service.delete_analysis(analysis_id, current_user)
    return None
