from __future__ import annotations

import simpy

from repairperson_simulator_app.simulator.job_priority_store import JobPriorityStore


class JobManager:
    """Manages the creation and scheduling of repair jobs."""

    def __init__(
        self,
        env: simpy.Environment,
        job_store: JobPriorityStore,
    ):
        self.env = env
        self.job_store = job_store
