from __future__ import annotations

from typing import TYPE_CHECKING

from repairperson_simulator_app.constants.enums import MachineStatus
from repairperson_simulator_app.events.base import Event


if TYPE_CHECKING:
    from repairperson_simulator_app.simulator.entities import Job


class BaseJobEventDetails(dict):

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


# -------------------- ASSIGNED --------------------
class OnJobAssignedEventDetails(BaseJobEventDetails):

    def __init__(self, job: Job):
        super().__init__(job)
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
