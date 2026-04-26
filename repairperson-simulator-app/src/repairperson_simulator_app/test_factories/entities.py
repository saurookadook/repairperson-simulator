from __future__ import annotations

import factory

from repairperson_simulator_app.constants import JobType
from repairperson_simulator_app.simulator.entities import Job, Operator


class JobFactory(factory.Factory):
    class Meta:
        model = Job

    created_at_ts = 0.0
    id = factory.Sequence(lambda n: n)
    job_type = factory.Iterator([JobType.MECHANICAL_REPAIR, JobType.ELECTRICAL_REPAIR])
    machine_id = factory.Sequence(lambda n: n % 5)  # Assuming 5 machines
    planned_duration = 15.0  # in minutes
    remaining_duration = factory.LazyAttribute(lambda o: o.planned_duration)


class LowPriorityJobFactory(JobFactory):
    """
    SOFTWARE_UPDATE has severity=5 (lowest priority)
    """

    job_type = JobType.SOFTWARE_UPDATE


class HighPriorityJobFactory(JobFactory):
    """
    ELECTRICAL_REPAIR has severity=1 (highest priority)
    """

    job_type = JobType.ELECTRICAL_REPAIR
    planned_duration = 25.0  # in minutes


class OperatorFactory(factory.Factory):
    class Meta:
        model = Operator

    id = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: f"Operator_{n}")
    # repair_time = 30.0  # in minutes
    walk_rate = 1.3  # in meters per second
