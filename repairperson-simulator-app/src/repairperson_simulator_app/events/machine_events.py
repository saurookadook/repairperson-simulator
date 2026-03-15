from __future__ import annotations

from typing import TYPE_CHECKING

from repairperson_simulator_app.constants.enums import JobType, MachineStatus
from repairperson_simulator_app.events.base import Event


if TYPE_CHECKING:
    from repairperson_simulator_app.simulator.machine import Machine


class OnMachineBrokenEventDetails(dict):
    """Event triggered when a machine breaks down."""

    def __init__(self, machine: Machine, job_type: JobType, repair_time_in_min: float):
        self.job_type = job_type
        self.machine = machine
        self.repair_time_in_min = repair_time_in_min
        self.status = MachineStatus.BROKEN.value


class OnMachineBrokenEvent(Event):

    def __init__(
        self,
        type: str,
        timestamp: float,
        details: OnMachineBrokenEventDetails,
    ):
        machine = getattr(self, "details", {}).get("machine", None)
        if machine is None:
            raise ValueError("OnMachineBrokenEvent requires 'machine' in details.")

        super().__init__(type=type, timestamp=timestamp, details=details)
        self.details = details
