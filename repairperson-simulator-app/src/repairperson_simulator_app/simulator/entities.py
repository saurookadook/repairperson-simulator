from __future__ import annotations

from dataclasses import dataclass, field
from math import inf
from typing import Optional

from repairperson_simulator_app.constants import (
    JobID,
    JobPriority,
    JobType,
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
        `assigned_operator_ids` (`List[int]`): List of `Operator` IDs currently assigned to this job.\n
            Defaults to an empty list.

    Properties:
        priority (JobPriority): Computed priority of the job based on job type severity,
            remaining duration, and job ID. Used for job scheduling and ordering.
            Returns a ``tuple`` of ``(severity, inf, remaining_duration, id)``.
    """

    created_at_ts: float
    id: JobID
    job_type: JobType
    # TODO: should this just be `machine`?
    machine_id: int
    # TODO: rename `duration` to `service_time`
    planned_duration: WorkDuration
    remaining_duration: WorkDuration
    assigned_operator_ids: list[int] = field(default_factory=list)
    is_completed: bool = False

    @property
    def priority(self) -> JobPriority:
        return calc_job_priority(self)

    def append_unique(self, operator_id: int):
        if operator_id not in self.assigned_operator_ids:
            self.assigned_operator_ids.append(operator_id)

    def add_operator_and_recalc_service_time(self, operator_id: int):
        prev_op_count = len(self.assigned_operator_ids)
        self.append_unique(operator_id)
        self.recalc_remaining_service_time(prev_op_count)

    def remove_operator_and_recalc_service_time(self, operator_id: int):
        prev_op_count = len(self.assigned_operator_ids)
        self.assigned_operator_ids.remove(operator_id)
        self.recalc_remaining_service_time(prev_op_count)

    def recalc_remaining_service_time(self, prev_op_count: int):
        """Recalculates remaining service time based on number of assigned operators."""
        new_op_count = len(self.assigned_operator_ids)

        if prev_op_count == 0 or prev_op_count == new_op_count:
            return

        self.remaining_duration = self.remaining_duration * (
            prev_op_count / max(new_op_count, 1)
        )


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
    current_job: Job | None = None  # TODO: this might be easier than an `id`...?
    current_job_id: JobID | None = None
    is_busy: bool = False
    in_transit: bool = False
    machine_location: Optional[int] = None

    @property
    def current_job_priority(self) -> JobPriority | None:
        if self.current_job is None:
            return None
        return self.current_job.priority

    def get_machine_location(self) -> float:
        return self.machine_location if self.machine_location is not None else inf

    def get_distance_to_machine(self, machine_id: int) -> float:
        return abs(self.get_machine_location() - machine_id)

    def is_interruptible(self) -> bool:
        return not self.is_busy and not self.in_transit

    def is_available_for_job(self, job: Job) -> bool:
        return (
            self.is_interruptible()
            and self.current_job is not None
            and self.current_job.id != job.id
            and self.current_job_priority is not None
            and job.priority[:3] < self.current_job_priority[:3]
        )

    def update_for_arrival_at_machine(self, machine_id: int) -> Operator:
        self.in_transit = False
        self.is_busy = True
        self.machine_location = machine_id
        return self

    def update_for_job_start(self, job: Job) -> Operator:
        self.current_job = job
        self.current_job_id = job.id
        self.is_busy = True
        return self

    def update_for_job_complete(self) -> Operator:
        self.current_job = None
        self.current_job_id = None
        self.is_busy = False
        return self

    def is_closer_than_target_op(self, target_operator: Operator, job: Job) -> bool:
        own_distance = self.get_distance_to_machine(job.machine_id)
        target_distance = target_operator.get_distance_to_machine(job.machine_id)
        return own_distance < target_distance

    def should_be_considered_available_over_target_op(
        self, target_operator: Operator
    ) -> bool:
        """
        Returns ``True`` if both conditions are met for ``target_operator``:
        - is working on the same job as ``self`` operator
        - started working on the job after ``self`` operator (i.e., ``target_operator`` is
            "less committed" to the job than ``self`` operator)
            - this "committment" is determined by the order in which operators were assigned to the job
        """
        if self.current_job is None or target_operator.current_job is None:
            return False

        if self.current_job.id != target_operator.current_job.id:
            return False

        job_assigned_op_ids = target_operator.current_job.assigned_operator_ids

        return self.id in job_assigned_op_ids and job_assigned_op_ids.index(
            self.id
        ) < job_assigned_op_ids.index(target_operator.id)
