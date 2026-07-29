from typing import Dict, List
from app.core.config import settings
from .models import ResearchGap
from .exceptions import ConfidenceCalculationError
from app.core.logging import logger

class ConfidenceCalculator:
    """Calculates and normalizes confidence scores for detected research gaps."""
    
    def __init__(self, weights: Dict[str, float] = None):
        config = settings.gap_detection_config
        self.weights = weights if weights is not None else config.get("strategy_weights", {})
        self.version = "1.1" # Differentiates logic changes
        
    def calculate(self, gaps: List[ResearchGap]) -> List[ResearchGap]:
        """
        Adjusts the confidence of gaps based on strategy weights and normalizes them into [0.0, 1.0].
        Provides an explainable confidence_breakdown mapping strategy names to their contributions.
        """
        if not gaps:
            return gaps
            
        try:
            weighted_gaps = []
            for gap in gaps:
                strategies = [s.strip() for s in gap.strategy.split(",")]
                total_weighted_confidence = 0.0
                breakdown = {}
                
                # Apportion confidence linearly across all detected strategies based on their global weight
                for strategy_name in strategies:
                    weight = self.weights.get(strategy_name, 1.0)
                    contribution = gap.confidence * weight
                    breakdown[strategy_name] = contribution
                    total_weighted_confidence += contribution
                
                gap.confidence = total_weighted_confidence
                gap.confidence_breakdown = breakdown
                weighted_gaps.append(gap)
                
            # Normalize globally across all gaps
            max_conf = max(g.confidence for g in weighted_gaps)
            if max_conf > 0:
                for gap in weighted_gaps:
                    gap.confidence = gap.confidence / max_conf
                    gap.confidence = min(1.0, max(0.0, gap.confidence))
                    
                    # Normalize the explainability breakdown map accordingly
                    for strategy_name, contribution in gap.confidence_breakdown.items():
                        scaled_contribution = contribution / max_conf
                        gap.confidence_breakdown[strategy_name] = scaled_contribution
                    
            return weighted_gaps
        except Exception as e:
            raise ConfidenceCalculationError(f"Failed to calculate confidence: {e}") from e
