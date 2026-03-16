from __future__ import annotations

import simpy

from repairperson_simulator_app.events import Event
from repairperson_simulator_app.simulator.config import EngineConfig, OperatorConfig
from repairperson_simulator_app.simulator.entities import Operator
from repairperson_simulator_app.simulator.event_logger import EventLogger
from repairperson_simulator_app.simulator.job_priority_store import JobPriorityStore
from repairperson_simulator_app.utils.singleton_meta import SingletonMeta


class OperatorManager(metaclass=SingletonMeta):

    def __init__(
        self,
        engine_config: EngineConfig,
        env: simpy.Environment,
        event_logger: EventLogger,
        job_store: JobPriorityStore,
    ):
        self.engine_config = engine_config
        self.env = env
        self.event_logger = event_logger
        self.job_store = job_store

        self.operators = self.engine_config.operators
        self.operator_processes = [None] * len(self.operators)

    def handle_assign_operator(self, event: Event):
        pass

    def create_operator_process(self, operator: Operator):
        priority, job = yield self.job_store.get()
