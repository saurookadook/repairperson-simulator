from __future__ import annotations

from repairperson_simulator_app.constants.enums import MachineStatus
from repairperson_simulator_app.events.base import Event
from repairperson_simulator_app.simulator.machine import Machine


class OnMachineBrokenEventDetails(dict):
    """Event triggered when a machine breaks down."""

    def __init__(self, machine: Machine):
        self.machine = machine
        self.status = MachineStatus.BROKEN.value


class OnMachineBrokenEvent(Event):

    def __init__(
        self,
        type: str,
        timestamp: float,
        details: OnMachineBrokenEventDetails,
    ):
        super().__init__(type=type, timestamp=timestamp, details=details)
        machine = getattr(self, "details", {}).get("machine", None)

        if machine is None:
            raise ValueError("OnMachineBrokenEvent requires 'machine' in details.")

        self.details = OnMachineBrokenEventDetails(machine)
