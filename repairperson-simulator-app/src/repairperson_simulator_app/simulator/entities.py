from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from math import inf
from typing import Optional, Tuple


Severity = int
Deadline = float
WorkDuration = float
JobID = int
JobPriority = Tuple[Severity, Deadline, WorkDuration, JobID]


class JobType(Enum):
    ELECTRICAL = auto()
    MECHANICAL = auto()
    SOFTWARE = auto()


@dataclass
class Job:
    """Represents a repair job for a machine."""

    created_at_ts: float
    id: JobID
    job_type: JobType
    machine_id: int
    planned_duration: WorkDuration
    remaining_duration: WorkDuration
    assigned_operator_id: Optional[int] = None

    @property
    def priority(self) -> JobPriority:
        job_type_severity = JobType[self.job_type.name].value
        return (job_type_severity, inf, self.remaining_duration, self.id)


@dataclass
class Operator:
    """Represents a repairperson (operator)."""

    id: int
    name: str
    repair_time: float  # in minutes
    walk_rate: float  # in meters per second
