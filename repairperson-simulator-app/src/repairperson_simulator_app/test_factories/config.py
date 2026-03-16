import factory

from repairperson_simulator_app.simulator.config import (
    EngineConfig,
    JobConfig,
    MachineConfig,
    OperatorConfig,
    RootConfig,
)
from repairperson_simulator_app.simulator.entities import Operator
from repairperson_simulator_app.simulator.machine import Machine

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


class MachineConfigFactory(factory.Factory):
    class Meta:
        model = MachineConfig

    count = DEFAULT_MACHINE_COUNT


class OperatorConfigFactory(factory.Factory):
    class Meta:
        model = OperatorConfig

    count = DEFAULT_OPERATOR_COUNT
    walk_rate = 1.3


class EngineConfigFactory(factory.Factory):
    class Meta:
        model = EngineConfig

    horizon = 10080  # Minutes in a week
    machines = factory.List([])
    operators = factory.List([])


class RootConfigFactory(factory.Factory):
    class Meta:
        model = RootConfig

    machine_config = factory.SubFactory(MachineConfigFactory)
    mean_processing_time = 10.0
    mean_time_to_failure = 300.0
    operator_config = factory.SubFactory(OperatorConfigFactory)
    seed = 54320
    sigma_processing_time = 2.0


class HighFailureRateRootConfigFactory(RootConfigFactory):
    mean_time_to_failure = 30.0
