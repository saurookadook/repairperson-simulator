from __future__ import annotations

import pytest
import simpy
from typing import Callable

from repairperson_simulator_app.constants import EventType, JobType
from repairperson_simulator_app.events import (
    OnJobQueuedEventDetails,
    OnMachineBrokenEventDetails,
)
from repairperson_simulator_app.simulator.config import EngineConfig, RootConfig
from repairperson_simulator_app.simulator.event_logger import EventLogger
from repairperson_simulator_app.simulator.job_priority_store import JobPriorityStore
from repairperson_simulator_app.simulator.job_manager import JobManager
from repairperson_simulator_app.simulator.machine import Machine
from repairperson_simulator_app.simulator.randomizer import Randomizer
from repairperson_simulator_app.utils.event_observer import EventObserver


def test_job_manager_initialization(
    engine_config_factory: Callable[..., EngineConfig],
    env: simpy.Environment,
    event_logger: EventLogger,
    job_store: JobPriorityStore,
    randomizer_factory: Callable[..., Randomizer],
    root_config_factory: Callable[..., RootConfig],
):
    root_config = root_config_factory()
    randomizer = randomizer_factory(root_config)
    machines = [
        Machine(env, root_config, randomizer, id=i, name=f"Machine {i}")
        for i in range(root_config.machine_config.count)
    ]

    engine_config = engine_config_factory()
    engine_config.machines = machines
    job_manager = JobManager(env, engine_config, job_store)

    assert job_manager.engine_config == engine_config
    assert job_manager.env == env
    assert job_manager.event_logger == event_logger
    assert job_manager.job_store == job_store
    assert job_manager.machines == machines


def test_job_manager_handle_machine_failure_creates_and_schedules_job(
    mocker,
    engine_config_factory: Callable[..., EngineConfig],
    env: simpy.Environment,
    event_observer: EventObserver,
    job_store: JobPriorityStore,
    randomizer_factory: Callable[..., Randomizer],
    root_config_factory: Callable[..., RootConfig],
):
    root_config = root_config_factory()
    randomizer = randomizer_factory(root_config)
    machines = [
        Machine(env, root_config, randomizer, id=i, name=f"Machine {i}")
        for i in range(root_config.machine_config.count)
    ]

    engine_config = engine_config_factory()
    engine_config.machines = machines
    job_manager = JobManager(env, engine_config, job_store)

    spy = mocker.spy(job_manager, "handle_machine_failure")

    job_manager.setup_listeners()

    event_details = OnMachineBrokenEventDetails(
        machine=machines[0],
        job_type=JobType.MECHANICAL_REPAIR,
        repair_time_in_min=20.0,
    )

    job_store = job_manager.job_store
    assert len(job_store.items) == 0

    event_observer.dispatch_event(EventType.ON_MACHINE_BROKEN.value, event_details)

    assert spy.call_count == 1
    event_call_arg = spy.call_args[0][0]
    assert event_call_arg.type == EventType.ON_MACHINE_BROKEN.value
    assert event_call_arg.details.job_type == event_details.job_type
    assert event_call_arg.details.machine == event_details.machine
    assert event_call_arg.details.repair_time_in_min == event_details.repair_time_in_min
    assert event_call_arg.details.status == event_details.status

    assert len(job_store.items) == 1
    _, job = job_store.items[0]
    assert job.job_type == event_details.job_type
    assert job.machine_id == event_details.machine.id
    assert job.planned_duration == event_details.repair_time_in_min
    assert job.remaining_duration == event_details.repair_time_in_min


def test_job_manager_handle_machine_failure_dispatches_job_queued_event(
    mocker,
    engine_config_factory: Callable[..., EngineConfig],
    env: simpy.Environment,
    event_observer: EventObserver,
    job_store: JobPriorityStore,
    randomizer_factory: Callable[..., Randomizer],
    root_config_factory: Callable[..., RootConfig],
):
    root_config = root_config_factory()
    randomizer = randomizer_factory(root_config)
    machines = [
        Machine(env, root_config, randomizer, id=i, name=f"Machine {i}")
        for i in range(root_config.machine_config.count)
    ]

    engine_config = engine_config_factory()
    engine_config.machines = machines
    job_manager = JobManager(env, engine_config, job_store)

    job_manager.setup_listeners()

    dispatch_spy = mocker.spy(event_observer, "dispatch_event")

    event_details = OnMachineBrokenEventDetails(
        machine=machines[0],
        job_type=JobType.MECHANICAL_REPAIR,
        repair_time_in_min=20.0,
    )

    job_store = job_manager.job_store
    assert len(job_store.items) == 0

    event_observer.dispatch_event(EventType.ON_MACHINE_BROKEN.value, event_details)

    assert len(job_store.items) == 1

    assert dispatch_spy.call_count == 2
    job_queue_call_args = dispatch_spy.call_args_list[1]
    assert job_queue_call_args.args[0] == EventType.ON_JOB_QUEUED.value
    dispatch_call_details = job_queue_call_args.kwargs["details"]
    assert dispatch_call_details is not None
    assert isinstance(dispatch_call_details, OnJobQueuedEventDetails)
    assert dispatch_call_details.job.job_type == event_details.job_type
    assert dispatch_call_details.job.machine_id == event_details.machine.id
