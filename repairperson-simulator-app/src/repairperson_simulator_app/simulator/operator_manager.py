from __future__ import annotations

import simpy
from typing import List

from repairperson_simulator_app.simulator.config import OperatorConfig
from repairperson_simulator_app.simulator.entities import Operator


class OperatorManager:
    def __init__(self, env: simpy.Environment, operators: List[OperatorConfig]):
        self.env = env
        self.operators = [
            Operator(
                id=i,
                name=op_config.name,
                repair_time=op_config.repair_time,
                walk_rate=op_config.walk_rate,
            )
            for i, op_config in enumerate(operators)
        ]
