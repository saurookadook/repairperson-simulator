from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Optional, TypeVar


Details = TypeVar("Details")


@dataclass
class Event(Generic[Details]):
    type: str
    timestamp: float
    details: Optional[Details]
