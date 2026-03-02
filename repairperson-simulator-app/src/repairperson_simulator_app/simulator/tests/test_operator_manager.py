from __future__ import annotations

import pytest
import simpy

from repairperson_simulator_app.simulator.config import OperatorConfig
from repairperson_simulator_app.simulator.job_priority_store import JobPriorityStore
from repairperson_simulator_app.simulator.operator_manager import OperatorManager


def test_operator_manager_initialization(env: simpy.Environment):
    operator_configs = [
        OperatorConfig(name="Alice", repair_time=30.0, walk_rate=1.5),
        OperatorConfig(name="Bob", repair_time=25.0, walk_rate=1.2),
    ]

    job_store = JobPriorityStore(env)
    operator_manager = OperatorManager(env, job_store, operator_configs)

    assert len(operator_manager.operators) == 2
    for operator_config, operator in zip(operator_configs, operator_manager.operators):
        assert isinstance(operator.id, int)
        assert operator.name == operator_config.name
        assert operator.walk_rate == operator_config.walk_rate
        assert operator.current_job_id is None
