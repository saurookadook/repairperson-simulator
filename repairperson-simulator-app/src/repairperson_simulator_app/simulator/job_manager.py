from __future__ import annotations

import simpy
from itertools import count
from typing import List

from repairperson_simulator_app.events.base import Event
from repairperson_simulator_app.events.machine_events import OnMachineBrokenEventDetails
from repairperson_simulator_app.simulator.config import EngineConfig
from repairperson_simulator_app.simulator.entities import Job, calc_job_priority
from repairperson_simulator_app.simulator.machine import Machine
from repairperson_simulator_app.simulator.event_logger import EventLogger
from repairperson_simulator_app.simulator.job_priority_store import JobPriorityStore
from repairperson_simulator_app.utils.singleton_meta import SingletonMeta


class JobManager(metaclass=SingletonMeta):
    """Manages the creation and scheduling of repair jobs."""

    def __init__(
        self,
        env: simpy.Environment,
        engine_config: EngineConfig,
        job_store: JobPriorityStore,
    ):
        self.env = env
        self.engine_config = engine_config
        self.job_store = job_store
        self.machines = self.engine_config.machines

        self.event_logger = EventLogger(self.env)
        self.in_progress_jobs: List[Job] = []
        self._job_id = count()

    def add_job(self, job):
        priority = calc_job_priority(job)
        self.job_store.put((priority, job))

    def handle_machine_failure(self, event: Event[OnMachineBrokenEventDetails]):
        """Callback function for machine failures to create jobs accordingly."""
        if event.details is None or event.details.machine is None:
            raise ValueError(
                f"[{self.handle_machine_failure.__qualname__}] 'event' is missing details about broken machine."
            )

        job_id = next(self._job_id)
        job = Job(
            created_at_ts=self.env.now,
            id=job_id,
            job_type=event.details.job_type,
            machine_id=event.details.machine.id,
            planned_duration=event.details.repair_time_in_min,
            remaining_duration=event.details.repair_time_in_min,
        )
        self.job_store.put(job)
