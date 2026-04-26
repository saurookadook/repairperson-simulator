from __future__ import annotations

import logging
import pytest
import simpy
from collections import deque
from typing import TYPE_CHECKING, Any, Generator

from repairperson_simulator_app.constants import EventType
from repairperson_simulator_app.events.job_events import OnJobQueuedEventDetails
from repairperson_simulator_app.simulator.job_manager import JobManager
from repairperson_simulator_app.utils.event_observer import event_observer

if TYPE_CHECKING:
    from repairperson_simulator_app.simulator.entities import Job


local_logger: logging.Logger = logging.getLogger(__name__)

# TODO: delete me later :D
from rich import inspect as ri


def schedule_jobs(
    jobs: list[Job], job_manager: JobManager, env: simpy.Environment
) -> Generator[simpy.Timeout, Any, None]:
    jobs_queue = deque(jobs)

    while len(jobs_queue) > 0:
        job = jobs_queue.popleft()

        job_manager.put_job_to_store(job)
        event_observer.dispatch_event(
            EventType.ON_JOB_QUEUED.value,
            details=OnJobQueuedEventDetails(job),
        )

        if len(jobs_queue) > 0:
            yield env.timeout(jobs_queue[0].created_at_ts)


@pytest.mark.preemption
def test_operator_manager_handles_preemption_for_different_machines(
    env_and_root_config_factory, engine_config_factory, test_jobs, test_setup_factory
):
    """
    Tests that the operator manager correctly handles job preemption based on priority.

    Scenario:
    - A single operator starts working on a low-priority job (SOFTWARE_UPDATE) at machine 0.
    - While the operator is busy, a higher-priority job (ELECTRICAL_REPAIR) is queued at machine 1.
    - Since no other operators are available and the new job has higher priority,
      the operator's current work should be preempted.
    """
    env, root_config = env_and_root_config_factory(operator_config__count=1)
    engine_config = engine_config_factory(env, root_config)

    job_store, job_manager, operator_filter_store, operator_manager = (
        test_setup_factory(env, root_config, engine_config)
    )

    event_observer.reset_all_registered_events()
    operator_manager.setup_listeners()

    env.process(schedule_jobs(test_jobs, job_manager, env))
    env.run(until=20)

    low_priority_job = test_jobs[0]
    high_priority_job = test_jobs[1]

    assert (
        not low_priority_job.is_completed
    ), "Low-priority job should not have been completed (preempted by higher priority job)"
    assert (
        low_priority_job.remaining_duration > 0
    ), "Low-priority job should have remaining work after preemption"
    assert (
        low_priority_job.remaining_duration < low_priority_job.planned_duration
    ), "Low-priority job should have had some work done before preemption"

    operator = operator_filter_store.get_operator_by_id(0)
    assert operator.is_busy, "Operator should be busy after preemption"
    assert (
        operator.current_job is high_priority_job
    ), "Operator should be working on the high-priority job after preemption"

    assert (
        low_priority_job in job_store
    ), "Low-priority job should still be in the job store"
    assert (
        high_priority_job not in job_store
    ), "High-priority job should have been removed from the job store for assignment"


@pytest.mark.preemption
def test_operator_manager_handles_preemption_exits_at_horizon(
    env_and_root_config_factory, engine_config_factory, test_jobs, test_setup_factory
):
    """
    Tests that the operator manager correctly handles job preemption based on
    priority but exits at the simulation horizon.
    """
    env, root_config = env_and_root_config_factory(operator_config__count=1)
    engine_config = engine_config_factory(env, root_config)

    job_store, job_manager, operator_filter_store, operator_manager = (
        test_setup_factory(env, root_config, engine_config)
    )

    event_observer.reset_all_registered_events()
    operator_manager.setup_listeners()

    env.process(schedule_jobs(test_jobs, job_manager, env))
    env.run(until=20)

    low_priority_job = test_jobs[0]
    high_priority_job = test_jobs[1]

    assert (
        not low_priority_job.is_completed
    ), "Low-priority job should not have been completed (preempted by higher priority job)"
    assert (
        low_priority_job.remaining_duration > 0
    ), "Low-priority job should have remaining work after preemption"
    assert (
        low_priority_job.remaining_duration < low_priority_job.planned_duration
    ), "Low-priority job should have had some work done before preemption"

    operator = operator_filter_store.get_operator_by_id(0)
    assert operator.is_busy, "Operator should be busy after preemption"
    assert (
        operator.current_job is high_priority_job
    ), "Operator should be working on the high-priority job after preemption"

    assert (
        low_priority_job in job_store
    ), "Low-priority job should still be in the job store"
    assert (
        high_priority_job not in job_store
    ), "High-priority job should have been removed from the job store for assignment"


@pytest.mark.preemption
def test_operator_manager_handles_preemption_for_different_machines_and_resumes_preempted_jobs(
    env_and_root_config_factory, engine_config_factory, test_jobs, test_setup_factory
):
    """
    Tests that the operator manager correctly handles job preemption based on priority.

    Scenario:
    - A single operator starts working on a low-priority job (SOFTWARE_UPDATE) at machine 0.
    - While the operator is busy, a higher-priority job (ELECTRICAL_REPAIR) is queued at machine 1.
    - Since no other operators are available and the new job has higher priority,
      the operator's current work should be preempted.
    - After the operator completes the high-priority job, they should resume work on the
      preempted low-priority job.
    """
    env, root_config = env_and_root_config_factory(operator_config__count=1)
    engine_config = engine_config_factory(env, root_config)

    job_store, job_manager, operator_filter_store, operator_manager = (
        test_setup_factory(env, root_config, engine_config)
    )

    event_observer.reset_all_registered_events()
    operator_manager.setup_listeners()

    env.process(schedule_jobs(test_jobs, job_manager, env))
    env.run(until=32)

    low_priority_job = test_jobs[0]
    high_priority_job = test_jobs[1]

    assert (
        high_priority_job.is_completed
    ), "High-priority job should have been completed by the operator"
    assert (
        high_priority_job.remaining_duration == 0
    ), "High-priority job should have no remaining work after completion"

    operator = operator_filter_store.get_operator_by_id(0)
    assert operator.is_busy, "Operator should be busy after preemption"
    assert (
        operator.current_job is low_priority_job
    ), "Operator should have resumed the low-priority job after completing the high-priority job"

    assert (
        high_priority_job not in job_store
    ), "High-priority job should not be in the job store because it was completed"
    assert (
        low_priority_job not in job_store
    ), "Low-priority job should not be in the job store because it's assigned to the operator"


@pytest.mark.preemption
def test_operator_manager_handles_preemption_for_multiple_operators():
    """
    Tests that the operator manager correctly handles job preemption based on priority
    for multiple operators across multiple machines.

    Tests following scenarios:
    - Free operators are prioritized during job assignment over busy operators.
    - Busy operators are preempted when no free operators are available AND when
        their current job is lower priority than the incoming job.
    - Busy operators are NOT preempted when their current job is higher priority
        than the incoming job.
    - Operators resume preempted jobs after completing higher priority jobs.
    """
    pass


@pytest.mark.preemption
def test_operator_manager_handles_preemption_TBD():
    pass
