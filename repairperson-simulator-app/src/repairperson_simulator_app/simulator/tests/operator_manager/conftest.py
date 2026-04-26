from __future__ import annotations

import pytest
import simpy
from typing import TYPE_CHECKING, Callable

from repairperson_simulator_app.constants import JobType
from repairperson_simulator_app.simulator.entities import Job, Operator
from repairperson_simulator_app.simulator.job_manager import JobManager
from repairperson_simulator_app.simulator.job_priority_store import JobPriorityStore
from repairperson_simulator_app.simulator.machine import Machine
from repairperson_simulator_app.simulator.machine_mediator import MachineMediator
from repairperson_simulator_app.simulator.operator_filter_store import (
    OperatorFilterStore,
)
from repairperson_simulator_app.simulator.operator_manager import OperatorManager
from repairperson_simulator_app.simulator.randomizer import Randomizer
from repairperson_simulator_app.test_factories.config import (
    EngineConfigFactory,
    RootConfigFactory,
)
from repairperson_simulator_app.test_factories.entities import (
    HighPriorityJobFactory,
    LowPriorityJobFactory,
)

if TYPE_CHECKING:
    from repairperson_simulator_app.simulator.config import EngineConfig, RootConfig


@pytest.fixture
def env_and_root_config_factory():
    def _factory(**root_config_kwargs) -> tuple[simpy.Environment, RootConfig]:
        env = simpy.Environment()
        root_config = RootConfigFactory(**root_config_kwargs)

        return env, root_config

    return _factory


@pytest.fixture
def test_jobs() -> list[Job]:
    low_priority_job = LowPriorityJobFactory(
        created_at_ts=0.0,
        id=0,
        machine_id=0,
        planned_duration=15.0,
    )
    high_priority_job = HighPriorityJobFactory(
        created_at_ts=5.0,
        id=1,
        machine_id=1,
        planned_duration=25.0,
    )

    return [low_priority_job, high_priority_job]


@pytest.fixture
def test_setup_factory() -> (
    Callable[
        ..., tuple[JobPriorityStore, JobManager, OperatorFilterStore, OperatorManager]
    ]
):
    def _factory(
        env: simpy.Environment, root_config: RootConfig, engine_config: EngineConfig
    ):
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

        return (job_store, job_manager, operator_filter_store, operator_manager)

    return _factory
