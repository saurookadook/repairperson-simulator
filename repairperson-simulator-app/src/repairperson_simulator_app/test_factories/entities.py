import factory

from repairperson_simulator_app.simulator.entities import Operator


class OperatorFactory(factory.Factory):
    class Meta:
        model = Operator

    id = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: f"Operator_{n}")
    # repair_time = 30.0  # in minutes
    walk_rate = 1.3  # in meters per second
