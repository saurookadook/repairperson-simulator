from __future__ import annotations

import simpy
from itertools import count
from simpy.resources.store import StoreGet, StorePut
from typing import TYPE_CHECKING

from repairperson_simulator_app.constants import EventType
from repairperson_simulator_app.events.base import Event
from repairperson_simulator_app.events.job_events import OnJobQueuedEventDetails
from repairperson_simulator_app.events.machine_events import OnMachineBrokenEventDetails
from repairperson_simulator_app.simulator.config import EngineConfig
from repairperson_simulator_app.simulator.entities import Job, calc_job_priority
from repairperson_simulator_app.simulator.event_logger import EventLogger
from repairperson_simulator_app.simulator.job_priority_store import JobPriorityStore
from repairperson_simulator_app.utils.event_observer import event_observer

if TYPE_CHECKING:
    from repairperson_simulator_app.simulator.machine import Machine


class JobManager:
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
        self.in_progress_jobs: list[Job] = []
        self._job_id = count()

    def get_next_job(self) -> StoreGet:
        return self.job_store.get()

    def put_job_to_store(self, job: Job, should_log: bool = True) -> StorePut:
        if should_log:
            # TODO: maybe unnecessary?
            self.event_logger.log_event(
                event_type=EventType.JOB_ADDED_TO_STORE.value,
                details=dict(
                    job_id=job.id,
                    job_type=job.job_type,
                    machine_id=job.machine_id,
                    job_planned_duration=job.planned_duration,
                    job_remaining_duration=job.remaining_duration,
                ),
            )

        priority = calc_job_priority(job)
        return self.job_store.put((priority, job))

    def re_put_job_to_store(self, job: Job) -> StorePut:
        return self.put_job_to_store(job, should_log=False)

    def setup_listeners(self):
        event_observer.add_event_listener(
            EventType.ON_MACHINE_BROKEN.value, self.handle_machine_failure
        )

    def update_completed_job(self, job: Job, machine: Machine):
        for op_id in job.assigned_operator_ids:
            # TODO: log something?
            pass
        # machine.current_job = None
        # jm_machine = self.machines[job.machine_id]

    def handle_machine_failure(self, event: Event[OnMachineBrokenEventDetails]):
        """Callback function for machine failures to create jobs accordingly."""
        if event.details is None or event.details.machine is None:
            raise ValueError(
                f"[{self.handle_machine_failure.__qualname__}] 'event' is missing details about broken machine."
            )

        machine = event.details.machine
        job_id = next(self._job_id)

        job = Job(
            created_at_ts=self.env.now,
            id=job_id,
            job_type=event.details.job_type,
            machine_id=machine.id,
            planned_duration=event.details.repair_time_in_min,
            remaining_duration=event.details.repair_time_in_min,
        )
        self.put_job_to_store(job)

        event_observer.dispatch_event(
            EventType.ON_JOB_QUEUED.value, details=OnJobQueuedEventDetails(job)
        )
