from __future__ import annotations

import simpy
from typing import List

from repairperson_simulator_app.simulator.config import OperatorConfig
from repairperson_simulator_app.simulator.entities import Operator
from repairperson_simulator_app.simulator.job_priority_store import JobPriorityStore


class OperatorManager:
    def __init__(
        self,
        env: simpy.Environment,
        job_store: JobPriorityStore,
        operators: List[OperatorConfig],
    ):
        self.env = env
        self.job_store = job_store
        self.operators = [
            Operator(
                id=i,
                name=op_config.name,
                walk_rate=op_config.walk_rate,
            )
            for i, op_config in enumerate(operators)
        ]
        self.operator_processes = [None] * len(self.operators)

    def create_operator_process(self, operator: Operator):
        priority, job = yield self.job_store.get()
