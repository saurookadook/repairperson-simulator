import logging
import pytest
import simpy
from rich import inspect
from typing import Callable

from repairperson_simulator_app.simulator.config import EngineConfig, RootConfig
from repairperson_simulator_app.simulator.event_logger import EventLogger
from repairperson_simulator_app.simulator.job_priority_store import JobPriorityStore
from repairperson_simulator_app.simulator.machine import Machine
from repairperson_simulator_app.simulator.randomizer import Randomizer
from repairperson_simulator_app.test_factories.config import (
    EngineConfigFactory,
    RootConfigFactory,
)
from repairperson_simulator_app.test_factories.entities import OperatorFactory
from repairperson_simulator_app.utils.event_observer import EventObserver
from repairperson_simulator_app.utils.logging import configure_logging


test_logger: logging.Logger = configure_logging("TEST_LOGGER")


@pytest.fixture(scope="session")
def rich_inspect():
    """Shortcut for `rich.inspect` in tests.

    Usage: `ri(my_object)`.
    """

    def wrapper(obj, **kwargs):
        return inspect(obj, **kwargs)

    return wrapper


@pytest.fixture
def event_observer() -> EventObserver:
    instance = EventObserver()
    instance.reset_all_registered_events()
    return instance


@pytest.fixture
def engine_config_factory() -> Callable[..., EngineConfig]:
    """Provides a default `EngineConfig` from `EngineConfigFactory` for tests."""

    def _factory(env, root_config) -> EngineConfig:
        randomizer = Randomizer(root_config=root_config)
        machines = [
            Machine(env, root_config, randomizer, id=index, name=f"Machine {index}")
            for index in range(root_config.machine_config.count)
        ]
        operators = [
            OperatorFactory(id=index, name=f"Operator {index}", walk_rate=0.0)
            for index in range(root_config.operator_config.count)
        ]

        engine_config = EngineConfigFactory(
            horizon_in_minutes=root_config.horizon_in_minutes,
            machines=machines,
            operators=operators,
        )

        return engine_config

    return _factory


@pytest.fixture
def env():
    """Provides a fresh SimPy `environment` for each test."""
    return simpy.Environment()


@pytest.fixture
def event_logger(env: simpy.Environment):
    """Provides an `EventLogger` for tests."""
    return EventLogger(env)


@pytest.fixture()
def job_store(env: simpy.Environment):
    """Provides a `JobPriorityStore` for tests."""
    store = JobPriorityStore(env)
    store.clear_items()
    return store


@pytest.fixture
def randomizer_factory() -> Callable[..., Randomizer]:
    """
    Provides a factory function to get a `Randomizer` for tests.
    If no `RootConfig` is provided, uses default values from `RootConfigFactory`.
    """

    def factory(root_config: RootConfig = RootConfigFactory()):
        return Randomizer(
            root_config=root_config,
        )

    return factory


@pytest.fixture
def root_config_factory() -> Callable[..., RootConfig]:
    """Provides a default `RootConfig` from `RootConfigFactory` for tests."""

    def factory(**kwargs) -> RootConfig:
        return RootConfigFactory(**kwargs)

    return factory
