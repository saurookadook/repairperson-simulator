from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from math import inf
from typing import Set, Tuple

from repairperson_simulator_app.constants.enums import JobType


Severity = int
Deadline = float
WorkDuration = float
JobID = int
JobPriority = Tuple[Severity, Deadline, WorkDuration, JobID]


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
        `remaining_duration` (WorkDuration): The remaining time needed to complete the job.\n
            _(units: minutes)_
        `assigned_operator_ids` (Set[int]): Set of `Operator` IDs currently assigned to this job.\n
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
        job_type_severity = JobType[self.job_type.name].value
        return (job_type_severity, inf, self.remaining_duration, self.id)


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
    # repair_time: float  # in minutes
    walk_rate: float  # in meters per second
