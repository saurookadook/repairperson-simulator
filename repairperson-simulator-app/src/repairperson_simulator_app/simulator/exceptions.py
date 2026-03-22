from __future__ import annotations

import simpy
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from repairperson_simulator_app.constants.enums import JobType
    from repairperson_simulator_app.constants.types import FaultType
    from repairperson_simulator_app.simulator.event_logger import EventLogger


class HorizonReached(simpy.Interrupt):
    """Exception raised when the simulation reaches its time horizon."""

    def __init__(
        self, message="Horizon reached", should_bubble: bool = False, **kwargs
    ):
        super().__init__(message, **kwargs)
        self.should_bubble = should_bubble


# TODO: is this necessary?
class MachineBrokenException(simpy.Interrupt):
    """Exception raised when a machine is broken and cannot operate."""

    def __init__(
        self,
        env: simpy.Environment,
        event_logger: EventLogger,
        *,
        fault_type: FaultType,
        job_type: JobType,
        machine_id: int,
        machine_name: str,
        planned_repair_time_in_min: float,
        **kwargs,
    ):
        self.planned_repair_time_in_min = planned_repair_time_in_min
        timestamp = env.now
        message = f"Machine '{machine_name}' is broken at {timestamp} minutes."
        event_logger.log_event(
            details=dict(
                machine_id=machine_id,
                machine_name=machine_name,
                job_type=job_type.name,
                planned_repair_time_in_min=planned_repair_time_in_min,
            ),
            event_type=fault_type,
        )

        super().__init__(
            message,
            **kwargs,
        )
