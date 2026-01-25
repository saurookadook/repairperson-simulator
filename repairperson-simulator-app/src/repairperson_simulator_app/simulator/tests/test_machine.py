from __future__ import annotations

import pytest
import simpy
from typing import Callable

from repairperson_simulator_app.simulator.machine import Machine
from repairperson_simulator_app.simulator.randomizer import Randomizer
from repairperson_simulator_app.test_factories.entities import OperatorFactory


def test_machine_initialization(
    env: simpy.Environment,
    randomizer_factory: Callable[..., Randomizer],
):
    randomizer = randomizer_factory()
    machine = Machine(id=1, name="Test Machine", env=env, randomizer=randomizer)

    assert machine.id == 1
    assert machine.name == "Test Machine"
    assert machine.env == env
    assert machine.randomizer == randomizer
    assert machine.is_broken is False


def test_machine_breakdown_process(
    env: simpy.Environment,
    randomizer_factory: Callable[..., Randomizer],
):
    randomizer = randomizer_factory()
    machine = Machine(id=1, name="Test Machine", env=env, randomizer=randomizer)

    machine.start_work(repairperson=OperatorFactory())

    simulation_duration = 1000  # seconds

    env.run(until=simulation_duration)

    assert machine.is_broken is True
