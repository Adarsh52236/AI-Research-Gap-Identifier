from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class Paper:
    title: str
    authors: List[str]
    abstract: str
    published_date: datetime
    categories: List[str]
    pdf_url: str
    source: str
    doi: Optional[str] = None
