from typing import Callable, List, Optional
from app.services.ingestion.models import Paper
from app.services.preprocessing.validator import validate_paper
from app.services.preprocessing.normalizer import normalize_paper
from app.core.logging import logger

class PaperPreprocessingPipeline:
    """
    Pipeline to orchestrate the validation and normalization of Paper objects.
    Maintains an ordered list of immutable processing stages.
    """
    def __init__(self, stages: Optional[List[Callable[[Paper], Paper]]] = None):
        if stages is None:
            self.stages = [
                validate_paper,
                normalize_paper
            ]
        else:
            self.stages = stages
            
    def process(self, paper: Paper) -> Paper:
        """
        Processes a single Paper object.
        Executes each stage sequentially.
        """
        logger.info("Pipeline start.")
        current_paper = paper
        
        for stage in self.stages:
            current_paper = stage(current_paper)
            
        logger.info("Pipeline completion successful.")
        return current_paper
