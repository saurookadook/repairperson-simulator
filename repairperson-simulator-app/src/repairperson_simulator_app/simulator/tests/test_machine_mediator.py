from __future__ import annotations

import pytest
import simpy
from typing import Callable

from repairperson_simulator_app.simulator.config import EngineConfig, RootConfig
from repairperson_simulator_app.simulator.event_logger import EventLogger
from repairperson_simulator_app.simulator.job_manager import JobManager
from repairperson_simulator_app.simulator.job_priority_store import JobPriorityStore
from repairperson_simulator_app.simulator.machine import Machine
from repairperson_simulator_app.simulator.machine_mediator import MachineMediator
from repairperson_simulator_app.simulator.randomizer import Randomizer


def test_machine_mediator_initialization(
    engine_config_factory: Callable[..., EngineConfig],
    env: simpy.Environment,
    root_config_factory: Callable[..., RootConfig],
):
    root_config = root_config_factory()
    machine_config = root_config.machine_config
    machines = [
        Machine(
            env=env,
            root_config=root_config,
            id=i,
            name=f"Machine {i}",
            randomizer=Randomizer(root_config=root_config),
        )
        for i in range(machine_config.count)
    ]

    engine_config = engine_config_factory()

    job_manager = JobManager(
        env,
        engine_config,
        job_store=JobPriorityStore(env),
    )

    mediator = MachineMediator(env, root_config, job_manager, machines)

    assert mediator.env == env
    assert mediator.root_config == root_config
    assert mediator.job_manager == job_manager
    assert mediator.machines == machines

    assert isinstance(mediator.event_logger, EventLogger)
    assert mediator.working_processes == []
