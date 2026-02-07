from __future__ import annotations

from enum import Enum


class EventType(Enum):
    ON_HORIZON_REACHED = "on_horizon_reached"
    ON_JOB_ASSIGNED = "on_job_assigned"
    ON_JOB_COMPLETED = "on_job_completed"
    ON_MACHINE_BROKEN = "on_machine_broken"
    ON_MACHINE_REPAIRED = "on_machine_repaired"
    ON_SIMULATION_STARTED = "on_simulation_started"
    ON_SIMULATION_ENDED = "on_simulation_ended"
