from dataclasses import dataclass
from typing import Optional

@dataclass
class EvidenceItem:
    """Represents a discrete piece of evidence supporting a research gap."""
    category: str
    message: str
    numeric_value: Optional[float] = None
