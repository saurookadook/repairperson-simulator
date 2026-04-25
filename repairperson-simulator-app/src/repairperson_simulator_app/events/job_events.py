from __future__ import annotations

from typing import TYPE_CHECKING

from repairperson_simulator_app.constants.enums import MachineStatus
from repairperson_simulator_app.events.base import Event, GenericEventDetails


if TYPE_CHECKING:
    from repairperson_simulator_app.simulator.entities import Job

# TODO: delete me later :D
from rich import inspect as ri
from rich.pretty import pretty_repr as pr


class BaseJobEventDetails(GenericEventDetails):

    def __init__(self, job: Job):
        self.job = job


class BaseJobEvent(Event):
    def __init__(
        self,
        event_type: str,
        timestamp: float,
        details: dict,
    ):
        if details is None:
            raise ValueError(
                f"`{self.__class__.__name__}` requires 'details' to be provided."
            )
        if getattr(details, "job", None) is None:
            raise ValueError(
                f"`{self.__class__.__name__}` requires 'job' in 'details'."
            )

        super().__init__(event_type, timestamp, details)
        self.details = details

    def get_csv_row(self) -> dict:
        evt_details = getattr(self, "details")

        return dict(
            event_type=self.type,
            timestamp=self.timestamp,
            job_id=evt_details.job.id,
            job_planned_duration=evt_details.job.planned_duration,
            job_remaining_duration=evt_details.job.remaining_duration,
            job_type=evt_details.job.job_type.value,
            machine_id=evt_details.job.machine_id,
            operator_id=evt_details.operator_id,
            status=evt_details.status,
        )


# -------------------- ASSIGNED --------------------
class OnJobAssignedEventDetails(BaseJobEventDetails):

    def __init__(self, job: Job, operator_id: int):
        super().__init__(job)
        self.operator_id = operator_id
        self.status = MachineStatus.BROKEN


class OnJobAssignedEvent(BaseJobEvent):
    """Event triggered when a job is assigned to an operator."""

    def __init__(
        self,
        event_type: str,
        timestamp: float,
        details: OnJobAssignedEventDetails,
    ):
        super().__init__(event_type, timestamp, details)
        # self.details = details


# -------------------- COMPLETED --------------------
class OnJobCompletedEventDetails(BaseJobEventDetails):

    def __init__(self, job: Job):
        super().__init__(job)
        self.status = MachineStatus.WORKING


class OnJobCompletedEvent(BaseJobEvent):
    """Event triggered when a job is completed."""

    def __init__(
        self,
        event_type: str,
        timestamp: float,
        details: OnJobCompletedEventDetails,
    ):
        super().__init__(event_type, timestamp, details)
        # self.details = details


# -------------------- QUEUED --------------------
class OnJobQueuedEventDetails(BaseJobEventDetails):

    def __init__(self, job: Job):
        super().__init__(job)
        self.status = MachineStatus.BROKEN


class OnJobQueuedEvent(BaseJobEvent):
    """Event triggered when a job is added to the job queue."""

    def __init__(
        self,
        event_type: str,
        timestamp: float,
        details: dict,
    ):
        super().__init__(event_type, timestamp, details)
        # self.details = details
