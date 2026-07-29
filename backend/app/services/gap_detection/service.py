import time
from typing import List, Dict
from app.core.logging import logger
from app.services.topic_modeling.models import TopicModelResult
from .base import GapDetectionStrategy
from .models import GapDetectionResult, ResearchGap
from .confidence import ConfidenceCalculator

class GapDetectionService:
    """Orchestrates multiple gap detection strategies to find research gaps."""
    
    def __init__(self, strategies: List[GapDetectionStrategy], calculator: ConfidenceCalculator = None):
        self.strategies = strategies
        self.calculator = calculator or ConfidenceCalculator()
        logger.info(f"GapDetectionService initialized with {len(strategies)} strategies.")
        
    def _merge_duplicate_gaps(self, gaps: List[ResearchGap]) -> List[ResearchGap]:
        """
        Merges gaps that target the same supporting topics and have similar strategies.
        """
        merged_map: Dict[str, ResearchGap] = {}
        for gap in gaps:
            topics_str = "-".join(map(str, sorted(gap.supporting_topics)))
            signature = f"{gap.title}_{topics_str}"
            
            if signature in merged_map:
                existing = merged_map[signature]
                existing.evidence.extend(gap.evidence)
                existing.confidence = max(existing.confidence, gap.confidence)
                if gap.strategy not in existing.strategy:
                    existing.strategy += f", {gap.strategy}"
            else:
                merged_map[signature] = gap
                
        return list(merged_map.values())

    def detect_gaps(self, topic_result: TopicModelResult) -> GapDetectionResult:
        """
        Executes all registered strategies against the provided topic model result,
        aggregates the detected gaps, merges duplicates, and calculates final confidence.
        """
        all_gaps: List[ResearchGap] = []
        total_start = time.perf_counter()
        
        for strategy in self.strategies:
            strategy_start = time.perf_counter()
            logger.info(f"Strategy '{strategy.name}' started.")
            
            try:
                gaps = strategy.detect(topic_result)
                all_gaps.extend(gaps)
                
                strategy_duration = time.perf_counter() - strategy_start
                logger.info(f"Strategy '{strategy.name}' finished in {strategy_duration:.4f}s. Detected {len(gaps)} gaps.")
            except Exception as e:
                logger.error(f"Strategy '{strategy.name}' failed: {e}")
                
        deduplicated_gaps = self._merge_duplicate_gaps(all_gaps)
        
        logger.info("Calculating final confidence for detected gaps.")
        final_gaps = self.calculator.calculate(deduplicated_gaps)
        
        # Log deep visibility into confidence distribution
        for gap in final_gaps:
            breakdown_str = ", ".join(f"{k}: {v:.2f}" for k, v in gap.confidence_breakdown.items())
            logger.info(
                f"Detected Gap: '{gap.title}' | Final Confidence: {gap.confidence:.2f} | "
                f"Breakdown: [{breakdown_str}]"
            )
        
        total_duration = time.perf_counter() - total_start
        logger.info(f"Gap detection execution completed in {total_duration:.4f}s. Total distinct gaps: {len(final_gaps)}")
        
        # Dynamic gap processing version signature
        c_version = getattr(self.calculator, "version", "1.0")
        
        return GapDetectionResult(
            total_gaps=len(final_gaps),
            gaps=final_gaps,
            confidence_version=c_version
        )
