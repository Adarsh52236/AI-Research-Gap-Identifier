import time
import json
import re
from datetime import datetime, timezone
from typing import List

from app.core.logging import logger
from .base import LLMProvider
from .prompt_builder import PromptBuilder
from .models import LLMTopicRefinement, LLMGapRefinement, LLMExecutiveSummary, LLMKeyFinding
from .exceptions import LLMReasoningError

def _parse_json_response(raw: str) -> dict:
    """Helper to extract and parse JSON from an LLM response."""
    try:
        # Try direct parse first
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    
    # Try finding markdown JSON block
    match = re.search(r'```(?:json)?(.*?)```', raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass
            
    # Try finding first { and last }
    start = raw.find('{')
    end = raw.rfind('}')
    if start != -1 and end != -1:
        try:
            return json.loads(raw[start:end+1])
        except json.JSONDecodeError:
            pass
            
    raise ValueError(f"Could not extract JSON from LLM response: {raw[:100]}...")


class LLMReasoningService:
    """Synthesis Engine for AI Research Analysis."""
    
    def __init__(self, prompt_builder: PromptBuilder, provider: LLMProvider):
        self.prompt_builder = prompt_builder
        self.provider = provider
        logger.info(f"LLM Synthesis Engine initialized with provider: {self.provider.name}")
        
    def refine_topic(self, raw_name: str, abstracts: List[str]) -> LLMTopicRefinement:
        """Phase 1: Refines a raw topic cluster into human-readable data."""
        logger.info(f"Refining topic: {raw_name}")
        prompt = self.prompt_builder.build_topic_refinement(raw_name, abstracts)
        
        try:
            raw_response = self.provider.generate(prompt)
            data = _parse_json_response(raw_response)
            return LLMTopicRefinement(
                name=data.get("name", raw_name),
                description=data.get("description", "No description provided."),
                keywords=data.get("keywords", [])
            )
        except Exception as e:
            logger.error(f"Failed to refine topic {raw_name}: {e}")
            # Fallback
            return LLMTopicRefinement(
                name=raw_name,
                description="Failed to generate description.",
                keywords=[]
            )

    def refine_gap(self, gap_id: str, gap_title: str, gap_desc: str, topics: List[str], abstracts: List[str]) -> LLMGapRefinement:
        """Phase 2: Refines an algorithmically detected gap into a rigorous academic finding."""
        logger.info(f"Refining gap: {gap_title}")
        prompt = self.prompt_builder.build_gap_refinement(gap_title, gap_desc, topics, abstracts)
        
        try:
            raw_response = self.provider.generate(prompt)
            data = _parse_json_response(raw_response)
            return LLMGapRefinement(
                gap_id=gap_id,
                title=data.get("title", gap_title),
                description=data.get("description", gap_desc),
                reasoning=data.get("reasoning", "No reasoning provided."),
                future_directions=data.get("future_directions", [])
            )
        except Exception as e:
            logger.error(f"Failed to refine gap {gap_title}: {e}")
            return LLMGapRefinement(
                gap_id=gap_id,
                title=gap_title,
                description=gap_desc,
                reasoning="Failed to generate reasoning.",
                future_directions=[]
            )

    def generate_executive_summary(self, query: str, topics: List[str], gaps: List[str]) -> LLMExecutiveSummary:
        """Phase 3: Synthesizes the global research story."""
        logger.info(f"Generating executive summary for query: {query}")
        prompt = self.prompt_builder.build_executive_summary(query, topics, gaps)
        
        try:
            raw_response = self.provider.generate(prompt)
            data = _parse_json_response(raw_response)
            
            key_findings = []
            for kf in data.get("key_findings", []):
                key_findings.append(LLMKeyFinding(
                    title=kf.get("title", "Finding"),
                    description=kf.get("description", ""),
                    importance=kf.get("importance", "Medium")
                ))
                
            return LLMExecutiveSummary(
                text=data.get("text", "Failed to generate executive summary."),
                key_findings=key_findings
            )
        except Exception as e:
            logger.error(f"Failed to generate executive summary: {e}")
            return LLMExecutiveSummary(
                text="The analysis pipeline was unable to synthesize a global executive summary. Please review the topics and gaps manually.",
                key_findings=[]
            )
