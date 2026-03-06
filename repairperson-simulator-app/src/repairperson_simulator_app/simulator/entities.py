from __future__ import annotations

from dataclasses import dataclass, field
from math import inf
from typing import TYPE_CHECKING, Optional, Set

from repairperson_simulator_app.constants import JobType

if TYPE_CHECKING:
    from repairperson_simulator_app.constants.types import (
        JobID,
        JobPriority,
        WorkDuration,
    )


@dataclass
class Job:
    """
    Represents a maintenance or repair job in the simulator.

    Attributes:
        `created_at_ts` (`float`): Timestamp when the job was created.
        `id` (`JobID`): Unique identifier for the job.
        `job_type` (`JobType`): The type/category of the job _(e.g., repair, maintenance)_.
        `machine_id` (`int`): ID of the machine this job is associated with.
        `planned_duration` (`WorkDuration`): The originally planned duration for completing the job.\n
            _(units: minutes)_
        `remaining_duration` (`WorkDuration`): The remaining time needed to complete the job.\n
            _(units: minutes)_
        `assigned_operator_ids` (`Set[int]`): Set of `Operator` IDs currently assigned to this job.\n
            Defaults to an empty `set`.

    Properties:
        priority (JobPriority): Computed priority of the job based on job type severity,
            remaining duration, and job ID. Used for job scheduling and ordering.
            Returns a tuple of (severity, inf, remaining_duration, id).
    """

    created_at_ts: float
    id: JobID
    job_type: JobType
    machine_id: int
    planned_duration: WorkDuration
    remaining_duration: WorkDuration
    assigned_operator_ids: Set[int] = field(default_factory=set)

    @property
    def priority(self) -> JobPriority:
        return calc_job_priority(self)


def calc_job_priority(
    job: Job,
) -> JobPriority:
    job_type = job.job_type
    job_type_severity = JobType[job_type.name].value
    return (job_type_severity, inf, job.remaining_duration, job.id)


@dataclass
class Operator:
    """Represents a repairperson (operator)."""

    id: int
    name: str
    walk_rate: float  # in meters per second
    current_job_id: JobID | None = None
    system_location: Optional[int] = None
