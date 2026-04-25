from __future__ import annotations

from typing import TYPE_CHECKING, cast

from repairperson_simulator_app.constants.enums import JobType, MachineStatus
from repairperson_simulator_app.events.base import Event, GenericEventDetails


if TYPE_CHECKING:
    from repairperson_simulator_app.simulator.machine import Machine


class OnMachineBrokenEventDetails(GenericEventDetails):
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
        if details is None:
            raise ValueError(
                f"`{self.__class__.__name__}` requires 'details' argument."
            )
        if getattr(details, "machine", None) is None:
            raise ValueError(
                f"`{self.__class__.__name__}` - 'details' requires 'machine' attribute."
            )
        if getattr(details, "job_type", None) is None:
            raise ValueError(
                f"`{self.__class__.__name__}` - 'details' requires 'job_type' attribute."
            )
        if getattr(details, "repair_time_in_min", None) is None:
            raise ValueError(
                f"`{self.__class__.__name__}` - 'details' requires 'repair_time_in_min' attribute."
            )

        super().__init__(type=type, timestamp=timestamp, details=details)
        self.details = details

    def get_csv_row(self) -> dict:
        evt_details = cast(OnMachineBrokenEventDetails, self.details)

        return dict(
            event_type=self.type,
            timestamp=self.timestamp,
            job_type=evt_details.job_type.value,
            machine_id=evt_details.machine.id,
            machine_name=evt_details.machine.name,
            machine_parts_made=evt_details.machine.parts_made,
            repair_time_in_min=evt_details.repair_time_in_min,
            status=evt_details.status,
        )
