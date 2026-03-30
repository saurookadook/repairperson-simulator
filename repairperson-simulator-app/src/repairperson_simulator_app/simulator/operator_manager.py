from __future__ import annotations

import simpy

from repairperson_simulator_app.constants import EventType
from repairperson_simulator_app.events import Event
from repairperson_simulator_app.simulator.config import EngineConfig
from repairperson_simulator_app.simulator.entities import Operator
from repairperson_simulator_app.simulator.event_logger import EventLogger
from repairperson_simulator_app.simulator.job_manager import JobManager
from repairperson_simulator_app.simulator.job_priority_store import JobPriorityStore
from repairperson_simulator_app.utils.event_observer import event_observer


class OperatorManager:

    def __init__(
        self,
        engine_config: EngineConfig,
        env: simpy.Environment,
        job_manager: JobManager,
    ):
        self.engine_config = engine_config
        self.env = env
        self.job_manager = job_manager

        self.event_logger = EventLogger(self.env)
        self.operators = self.engine_config.operators
        self.operator_processes = [None] * len(self.operators)

    def setup_listeners(self):
        event_observer.add_event_listener(
            EventType.ON_JOB_QUEUED.value, self.handle_job_queued
        )
        event_observer.add_event_listener(
            EventType.ON_ASSIGN_OPERATOR_TO_JOB.value,
            self.handle_assign_operator_to_job,
        )

    def handle_job_queued(self, event: Event):
        pass

    def handle_assign_operator_to_job(self, event: Event):
        pass

    def create_operator_process(self, operator: Operator):
        priority, job = yield self.job_manager.job_store.get()
