from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Event:
    type: str
    timestamp: float
    details: Optional[dict] = field(default_factory=dict)
