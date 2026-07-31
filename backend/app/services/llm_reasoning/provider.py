import json
from .base import LLMProvider

class MockLLMProvider(LLMProvider):
    """A placeholder LLM provider that returns deterministic mock responses."""
    
    @property
    def name(self) -> str:
        return "MockLLM-v1"
        
    def generate(self, prompt: str) -> str:
        """
        Returns a deterministic JSON-formatted string simulating a highly professional LLM response.
        Avoids external API calls and databases.
        """
        mock_response = {
            "summary": "This research gap represents a critical intersection between established theoretical frameworks and emerging empirical applications. The synthesis of the provided evidence indicates a systemic limitation in current methodologies, primarily driven by the inability of existing models to effectively generalize across heterogeneous datasets. Addressing this gap is of paramount importance for both academic literature and industrial deployment, as it directly impedes the robustness and scalability of state-of-the-art architectures.",
            "research_opportunities": [
                "Investigate novel regularization techniques to mitigate domain shift within heterogeneous datasets.",
                "Develop a hybrid neuro-symbolic framework capable of integrating explicit domain knowledge with implicit learned representations."
            ],
            "future_directions": [
                "Conduct large-scale longitudinal studies to empirically validate the stability of the proposed architectures across diverse operational environments.",
                "Explore cross-domain transferability through the lens of meta-learning and few-shot adaptation paradigms."
            ],
            "limitations": [
                "High initial computational overhead required for the proposed hybrid training methodologies.",
                "Significant dependence on the availability of high-quality, annotated heterogeneous datasets, which may introduce severe curation bottlenecks."
            ]
        }
        return json.dumps(mock_response)
