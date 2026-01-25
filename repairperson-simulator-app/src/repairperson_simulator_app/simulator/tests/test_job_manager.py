from __future__ import annotations

import pytest
import simpy

from repairperson_simulator_app.simulator.job_priority_store import JobPriorityStore
from repairperson_simulator_app.simulator.job_manager import JobManager


def test_job_manager_initialization(
    env: simpy.Environment, job_store: JobPriorityStore
):
    job_manager = JobManager(env, job_store)

    assert job_manager.env == env
    assert job_manager.job_store == job_store
