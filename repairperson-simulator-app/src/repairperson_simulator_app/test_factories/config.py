from __future__ import annotations

import factory
from typing import Optional

from repairperson_simulator_app.constants import JobType
from repairperson_simulator_app.simulator.config import (
    EngineConfig,
    FaultConfig,
    FaultDistributionConfig,
    JobConfig,
    MachineConfig,
    OperatorConfig,
    RootConfig,
)

# TODO: better solution for this?
DEFAULT_MACHINE_COUNT = 5
DEFAULT_OPERATOR_COUNT = 2


class JobConfigFactory(factory.Factory):
    class Meta:
        model = JobConfig

    machine_id = factory.Sequence(lambda n: n)
    operator_id = factory.Sequence(lambda n: n)
    planned_duration = 30.0
    remaining_duration = 30.0


class FaultDistributionConfigFactory(factory.Factory):
    class Meta:
        model = FaultDistributionConfig

    set_time: Optional[float] = 10.0
    cv: Optional[float] = 0.2


class FaultConfigFactory(factory.Factory):
    class Meta:
        model = FaultConfig

    distribution_cfg = factory.SubFactory(FaultDistributionConfigFactory)
    job_type: JobType = JobType.SOFTWARE_UPDATE


class MachineConfigFactory(factory.Factory):
    class Meta:
        model = MachineConfig

    count = DEFAULT_MACHINE_COUNT


class OperatorConfigFactory(factory.Factory):
    class Meta:
        model = OperatorConfig

    count = DEFAULT_OPERATOR_COUNT
    walk_rate = 1.3


class RootConfigFactory(factory.Factory):
    class Meta:
        model = RootConfig

    fault_rngs_map = factory.LazyFunction(dict)
    fault_types_map = factory.LazyFunction(
        lambda: dict(
            ARM_FAILURE=FaultConfigFactory(
                distribution_cfg=FaultDistributionConfigFactory(
                    set_time=10.0,
                    cv=0.2,
                ),
                job_type=JobType.MECHANICAL_MAINTENANCE,
            ),
            LOOSE_WIRE=FaultConfigFactory(
                distribution_cfg=FaultDistributionConfigFactory(
                    set_time=20.0,
                    cv=0.4,
                ),
                job_type=JobType.ELECTRICAL_MAINTENANCE,
            ),
            SOFTWARE_FAILURE=FaultConfigFactory(
                distribution_cfg=FaultDistributionConfigFactory(
                    set_time=5.0,
                    cv=0.1,
                ),
                job_type=JobType.SOFTWARE_UPDATE,
            ),
        )
    )
    machine_config = factory.SubFactory(MachineConfigFactory)
    operator_config = factory.SubFactory(OperatorConfigFactory)
    seed = 54320


class HighFailureRateRootConfigFactory(RootConfigFactory):
    # mean_time_to_failure = 30.0
    pass


class EngineConfigFactory(factory.Factory):
    class Meta:
        model = EngineConfig

    horizon_in_minutes = 10080  # Minutes in a week
    machines = factory.List([])
    operators = factory.List([])
