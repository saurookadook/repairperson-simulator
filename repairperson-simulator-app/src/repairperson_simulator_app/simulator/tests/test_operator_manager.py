from __future__ import annotations

import pytest
import simpy

from repairperson_simulator_app.simulator.config import EngineConfig, RootConfig
from repairperson_simulator_app.simulator.entities import Operator
from repairperson_simulator_app.simulator.event_logger import EventLogger
from repairperson_simulator_app.simulator.job_priority_store import JobPriorityStore
from repairperson_simulator_app.simulator.operator_manager import OperatorManager


def test_operator_manager_initialization(
    engine_config: EngineConfig, env: simpy.Environment, root_config: RootConfig
):
    op_config = root_config.operator_config
    op_config.count = 3
    op_config.walk_rate = 1.2

    engine_config.operators = [
        Operator(id=i, name=f"Operator {i}", walk_rate=op_config.walk_rate)
        for i in range(op_config.count)
    ]

    job_store = JobPriorityStore(env)
    operator_manager = OperatorManager(engine_config, env, job_store)

    assert len(operator_manager.operators) == op_config.count
    for i, operator in enumerate(operator_manager.operators):
        assert operator.id == i
        assert operator.name == f"Operator {i}"
        assert operator.walk_rate == op_config.walk_rate
        assert operator.current_job_id is None
