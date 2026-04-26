from __future__ import annotations

import pytest
import simpy
from typing import Callable

from repairperson_simulator_app.simulator.config import EngineConfig, RootConfig
from repairperson_simulator_app.simulator.entities import Operator
from repairperson_simulator_app.simulator.event_logger import EventLogger
from repairperson_simulator_app.simulator.job_manager import JobManager
from repairperson_simulator_app.simulator.job_priority_store import JobPriorityStore
from repairperson_simulator_app.simulator.machine_mediator import MachineMediator
from repairperson_simulator_app.simulator.operator_filter_store import (
    OperatorFilterStore,
)
from repairperson_simulator_app.simulator.operator_manager import OperatorManager


def test_operator_manager_initialization(
    engine_config_factory: Callable[..., EngineConfig],
    env: simpy.Environment,
    root_config_factory: Callable[..., RootConfig],
):
    root_config = root_config_factory()
    op_config = root_config.operator_config
    op_config.count = 3
    op_config.walk_rate = 1.2

    engine_config = engine_config_factory(env, root_config)
    engine_config.operators = [
        Operator(id=i, name=f"Operator {i}", walk_rate=op_config.walk_rate)
        for i in range(op_config.count)
    ]

    job_store = JobPriorityStore(env)
    job_manager = JobManager(env, engine_config, job_store)
    machine_mediator = MachineMediator(
        env, root_config, job_manager, engine_config.machines
    )
    operator_filter_store = OperatorFilterStore(env, engine_config)
    operator_manager = OperatorManager(
        env,
        engine_config,
        root_config,
        job_manager,
        machine_mediator,
        operator_filter_store,
    )

    assert len(operator_manager.operators) == op_config.count
    for i, operator in enumerate(operator_manager.operators):
        assert operator.id == i
        assert operator.name == f"Operator {i}"
        assert operator.walk_rate == op_config.walk_rate
        assert operator.current_job is None


def test_operator_manager_should_work_be_preempted_two_ops_other_op_free():
    pass


def test_operator_manager_should_work_be_preempted_two_ops_same_job():
    pass


def test_operator_manager_should_work_be_preempted_two_ops_same_job_priority_different_locations():
    pass


def test_operator_manager_should_work_be_preempted_two_ops_equidistant_different_job_priorities():
    pass


def test_operator_manager_should_work_be_preempted_two_ops_both_have_higher_priority_jobs():
    pass


def test_operator_manager_is_closest_interruptible_operator_to_machine():
    pass
