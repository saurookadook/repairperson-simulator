import logging
import pytest
import simpy
from rich import inspect
from typing import Callable

from repairperson_simulator_app.simulator.config import RootConfig
from repairperson_simulator_app.simulator.event_logger import EventLogger
from repairperson_simulator_app.simulator.job_priority_store import JobPriorityStore
from repairperson_simulator_app.simulator.randomizer import Randomizer
from repairperson_simulator_app.test_factories.config import (
    EngineConfigFactory,
    RootConfigFactory,
)
from repairperson_simulator_app.utils.event_observer import EventObserver
from repairperson_simulator_app.utils.logging import configure_logging

test_logger: logging.Logger = configure_logging("TEST_LOGGER")


@pytest.fixture(scope="session")
def rich_inspect():
    def wrapper(obj, **kwargs):
        return inspect(obj, **kwargs)

    return wrapper


@pytest.fixture
def event_observer() -> EventObserver:
    return EventObserver()


@pytest.fixture
def engine_config():
    """Provides a default `EngineConfig` from `EngineConfigFactory` for tests."""
    return EngineConfigFactory()


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
    return JobPriorityStore(env)


@pytest.fixture
def randomizer_factory() -> Callable[..., Randomizer]:
    """
    Provides a factory function to get a `Randomizer` for tests.
    If no `RootConfig` is provided, uses default values from `RootConfigFactory`.
    """

    def factory(root_config: RootConfig = RootConfigFactory()):
        return Randomizer(
            mean_processing_time=root_config.mean_processing_time,
            mean_time_to_failure=root_config.mean_time_to_failure,
            sigma_processing_time=root_config.sigma_processing_time,
        )

    return factory
