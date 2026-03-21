from __future__ import annotations

import pytest
import simpy
from typing import TYPE_CHECKING, Callable

from repairperson_simulator_app.simulator.machine import Machine
from repairperson_simulator_app.simulator.randomizer import Randomizer
from repairperson_simulator_app.test_factories.config import (
    HighFailureRateRootConfigFactory,
)

if TYPE_CHECKING:
    from repairperson_simulator_app.simulator.config import RootConfig


def test_machine_initialization(
    env: simpy.Environment,
    randomizer_factory: Callable[..., Randomizer],
    root_config_factory: Callable[..., RootConfig],
):
    root_config = root_config_factory()
    randomizer = randomizer_factory(root_config)
    machine = Machine(env, root_config, randomizer, id=1, name="Test Machine")

    assert machine.id == 1
    assert machine.name == "Test Machine"
    assert machine.env == env
    assert machine.randomizer == randomizer
    assert machine.is_broken is False


def test_machine_breakdown_process(
    env: simpy.Environment,
    randomizer_factory: Callable[..., Randomizer],
):
    root_config = HighFailureRateRootConfigFactory()
    randomizer = randomizer_factory(root_config)
    machine = Machine(env, root_config, randomizer, id=1, name="Test Machine")

    machine.start_work()

    simulation_duration = 1000  # seconds

    env.run(until=simulation_duration)

    assert machine.is_broken is True
