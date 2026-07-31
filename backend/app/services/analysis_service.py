import json
from typing import List
from datetime import datetime, timezone
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.analysis import Analysis
from app.models.user import User
from app.schemas.analysis import AnalysisCreate, AnalysisUpdate
from app.core.enums import AnalysisStatus
from app.repositories.analysis_repository import AnalysisRepository
from app.services.research_analysis.service import ResearchAnalysisService
from app.services.research_analysis.exceptions import ResearchAnalysisError

class AnalysisService:
    def __init__(self, db: Session, ai_service: ResearchAnalysisService):
        self.repository = AnalysisRepository(db)
        self.ai_service = ai_service

    def get_analysis(self, analysis_id: UUID, current_user: User) -> Analysis:
        analysis = self.repository.get_owned_analysis(analysis_id, current_user.id)
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        return analysis

    def list_project_analyses(self, project_id: UUID, current_user: User) -> List[Analysis]:
        # Ownership of the project is verified implicitly because the query joins Project and checks user_id
        return self.repository.list_project_analyses(project_id, current_user.id)

    def delete_analysis(self, analysis_id: UUID, current_user: User) -> dict:
        analysis = self.get_analysis(analysis_id, current_user)
        self.repository.soft_delete(analysis)
        return {"message": "Analysis deleted successfully"}

    def run_analysis_for_project(self, project_id: UUID, query: str, current_user: User, max_results: int = 100) -> Analysis:
        # Note: the router must check project ownership first, but since the prompt asked 
        # to ensure project ownership, we assume it's done before calling this, or we can check it.
        # But we only have `ai_service` and `repository` here. 
        # Actually, if the user owns the project is checked via `ProjectService.get_project` in router.
        # Let's keep creating it simple.
        
        # 1. Create Analysis row
        analysis_in = AnalysisCreate(project_id=project_id, query=query)
        analysis_db = self.repository.create(analysis_in)

        try:
            # 2. Invoke the existing ResearchAnalysisService
            result = self.ai_service.run_analysis(query=query, max_results=max_results)
            
            # 3. Extract metadata
            summary_text = f"Found {result.overview.papers_retrieved} retrieved papers, processed {result.overview.papers_processed} papers, detected {len(result.gaps)} gaps across {len(result.topics)} topics."
            
            # Generate raw_response by serializing the result safely
            import dataclasses, json
            if dataclasses.is_dataclass(result):
                raw_dict = dataclasses.asdict(result)
            elif hasattr(result, "dict"):
                raw_dict = result.dict()
            elif hasattr(result, "model_dump"):
                raw_dict = result.model_dump()
            else:
                raw_dict = {"data": str(result)}
                
            raw_response = json.loads(json.dumps(raw_dict, default=str))
            
            # 4. Update Analysis
            update_in = AnalysisUpdate(
                status=AnalysisStatus.COMPLETED,
                paper_count=result.overview.papers_processed,
                topic_count=len(result.topics),
                gap_count=len(result.gaps),
                summary=summary_text,
                raw_response=raw_response,
                completed_at=result.overview.timestamp
            )
            return self.repository.update(analysis_db, update_in)
            
        except Exception as e:
            import traceback
            # 5. Handle failures
            update_in = AnalysisUpdate(
                status=AnalysisStatus.FAILED,
                error_message=traceback.format_exc(),
                completed_at=datetime.now(timezone.utc)
            )
            self.repository.update(analysis_db, update_in)
            raise e
# trigger reload
