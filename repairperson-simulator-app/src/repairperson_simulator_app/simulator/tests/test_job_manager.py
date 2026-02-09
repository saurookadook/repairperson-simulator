from __future__ import annotations

import pytest
import simpy
from typing import Callable

from repairperson_simulator_app.constants import EventType, MachineStatus
from repairperson_simulator_app.events import OnMachineBrokenEventDetails
from repairperson_simulator_app.simulator.config import EngineConfig
from repairperson_simulator_app.simulator.event_logger import EventLogger
from repairperson_simulator_app.simulator.job_priority_store import JobPriorityStore
from repairperson_simulator_app.simulator.job_manager import JobManager
from repairperson_simulator_app.simulator.machine import Machine
from repairperson_simulator_app.simulator.randomizer import Randomizer
from repairperson_simulator_app.utils.event_observer import EventObserver


def test_job_manager_initialization(
    engine_config: EngineConfig,
    env: simpy.Environment,
    event_logger: EventLogger,
    job_store: JobPriorityStore,
    randomizer_factory: Callable[..., Randomizer],
):
    randomizer = randomizer_factory()
    machines = [
        Machine(id=i, name=machine.name, env=env, randomizer=randomizer)
        for i, machine in enumerate(engine_config.machines)
    ]

    job_manager = JobManager(engine_config, env, event_logger, job_store, machines)

    assert job_manager.engine_config == engine_config
    assert job_manager.env == env
    assert job_manager.event_logger == event_logger
    assert job_manager.job_store == job_store
    assert job_manager.machines == machines


def test_job_manager_listen_for_machine_failures(
    mocker,
    engine_config: EngineConfig,
    env: simpy.Environment,
    event_logger: EventLogger,
    event_observer: EventObserver,
    job_store: JobPriorityStore,
    randomizer_factory: Callable[..., Randomizer],
):
    randomizer = randomizer_factory()
    machines = [
        Machine(id=i, name=machine.name, env=env, randomizer=randomizer)
        for i, machine in enumerate(engine_config.machines)
    ]

    job_manager = JobManager(engine_config, env, event_logger, job_store, machines)

    spy = mocker.spy(job_manager, "on_machine_failure")

    event_observer.add_event_listener(
        EventType.ON_MACHINE_BROKEN.value, job_manager.on_machine_failure
    )
    event_observer.dispatch_event(
        EventType.ON_MACHINE_BROKEN.value,
        OnMachineBrokenEventDetails(machine=machines[0]),
    )

    assert spy.call_count == 1
    event_call_arg = spy.call_args[0][0]
    assert event_call_arg.type == EventType.ON_MACHINE_BROKEN.value
    assert event_call_arg.details.machine == machines[0]
    assert event_call_arg.details.status == MachineStatus.BROKEN.value
