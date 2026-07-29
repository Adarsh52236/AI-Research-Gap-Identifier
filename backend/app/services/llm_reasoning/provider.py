import json
from .base import LLMProvider

class MockLLMProvider(LLMProvider):
    """A placeholder LLM provider that returns deterministic mock responses."""
    
    @property
    def name(self) -> str:
        return "MockLLM-v1"
        
    def generate(self, prompt: str) -> str:
        """
        Returns a deterministic JSON-formatted string matching the expected prompt output.
        Avoids external API calls and databases.
        """
        mock_response = {
            "summary": "This is a mock summary explaining why the provided evidence suggests a significant research gap. It indicates an intersection lacking in recent literature.",
            "research_opportunities": [
                "Investigate novel methodologies.",
                "Conduct comprehensive literature reviews in this specific intersection."
            ],
            "future_directions": [
                "Develop unified frameworks.",
                "Apply generative models to broader datasets."
            ],
            "limitations": [
                "Data scarcity may hinder initial experiments.",
                "Potential computational bottlenecks."
            ]
        }
        return json.dumps(mock_response)
