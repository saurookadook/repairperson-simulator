import factory

from repairperson_simulator_app.simulator.config import (
    EngineConfig,
    JobConfig,
    MachineConfig,
    OperatorConfig,
    RootConfig,
)


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

    name = factory.Sequence(lambda n: f"Machine_{n}")
    failure_rate = 0.01


class OperatorConfigFactory(factory.Factory):
    class Meta:
        model = OperatorConfig

    name = factory.Sequence(lambda n: f"Operator_{n}")
    repair_time = 30.0
    walk_rate = 1.3


class EngineConfigFactory(factory.Factory):
    class Meta:
        model = EngineConfig

    horizon = 10080  # Minutes in a week
    machines = factory.List(
        [factory.SubFactory(MachineConfigFactory) for _ in range(2)]
    )
    operators = factory.List(
        [factory.SubFactory(OperatorConfigFactory) for _ in range(2)]
    )


class RootConfigFactory(factory.Factory):
    class Meta:
        model = RootConfig

    mean_processing_time = 10.0
    mean_time_to_failure = 300.0
    number_of_machines = 5
    number_of_operators = 2
    seed = 54320
    sigma_processing_time = 2.0
