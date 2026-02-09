from __future__ import annotations

import simpy
from typing import List

from repairperson_simulator_app.simulator.config import EngineConfig
from repairperson_simulator_app.simulator.entities import Job, calc_job_priority
from repairperson_simulator_app.events.base import Event
from repairperson_simulator_app.events.machine_events import OnMachineBrokenEventDetails
from repairperson_simulator_app.simulator.machine import Machine
from repairperson_simulator_app.simulator.event_logger import EventLogger
from repairperson_simulator_app.simulator.job_priority_store import JobPriorityStore
from repairperson_simulator_app.utils.singleton_meta import SingletonMeta


class JobManager(metaclass=SingletonMeta):
    """Manages the creation and scheduling of repair jobs."""

    def __init__(
        self,
        engine_config: EngineConfig,
        env: simpy.Environment,
        event_logger: EventLogger,
        job_store: JobPriorityStore,
        machines: List[Machine],
    ):
        self.engine_config = engine_config
        self.env = env
        self.event_logger = event_logger
        self.job_store = job_store
        self.machines = machines
        self.in_progress_jobs: List[Job] = []

    def add_job(self, job):
        priority = calc_job_priority(job)
        self.job_store.put((priority, job))

    def on_machine_failure(self, event: Event[OnMachineBrokenEventDetails]):
        """Callback function for machine failures to create jobs accordingly."""
        pass  # Implementation would go here
