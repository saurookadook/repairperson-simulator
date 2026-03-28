from __future__ import annotations

from typing import TYPE_CHECKING

from repairperson_simulator_app.constants.enums import JobType, MachineStatus
from repairperson_simulator_app.events.base import Event


if TYPE_CHECKING:
    from repairperson_simulator_app.simulator.machine import Machine


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
        if getattr(details, "job_type", None) is None:
            raise ValueError(
                f"`{self.__class__.__name__}` requires 'job_type' in 'details'."
            )
        if getattr(details, "machine", None) is None:
            raise ValueError(
                f"`{self.__class__.__name__}` requires 'machine' in 'details'."
            )

        super().__init__(event_type, timestamp, details)
        self.details = details


# -------------------- ASSIGNED --------------------
class OnJobAssignedEventDetails(dict):
    """Event triggered when a job is assigned to an operator."""

    def __init__(self, job_type: JobType, machine: Machine):
        self.job_type = job_type
        self.machine = machine
        self.status = MachineStatus.BROKEN


class OnJobAssignedEvent(BaseJobEvent):

    def __init__(
        self,
        event_type: str,
        timestamp: float,
        details: OnJobAssignedEventDetails,
    ):
        super().__init__(event_type, timestamp, details)
        # self.details = details


# -------------------- COMPLETED --------------------
class OnJobCompletedEventDetails(dict):
    """Event triggered when a job is completed."""

    def __init__(self, job_type: JobType, machine: Machine):
        self.job_type = job_type
        self.machine = machine
        self.status = MachineStatus.WORKING


class OnJobCompletedEvent(BaseJobEvent):

    def __init__(
        self,
        event_type: str,
        timestamp: float,
        details: OnJobCompletedEventDetails,
    ):
        super().__init__(event_type, timestamp, details)
        # self.details = details


# -------------------- QUEUED --------------------
class OnJobQueuedEventDetails(dict):
    """Event triggered when a job is added to the job queue."""

    def __init__(self, job_type: JobType, machine: Machine):
        self.job_type = job_type
        self.machine = machine
        self.status = MachineStatus.BROKEN


class OnJobQueuedEvent(BaseJobEvent):

    def __init__(
        self,
        event_type: str,
        timestamp: float,
        details: dict,
    ):
        super().__init__(event_type, timestamp, details)
        # self.details = details
