import logging
import pytest
import simpy
from rich import inspect

from repairperson_simulator_app.utils.logging import configure_logging

test_logger: logging.Logger = configure_logging("TEST_LOGGER")


@pytest.fixture(scope="session")
def rich_inspect():
    def wrapper(obj, **kwargs):
        return inspect(obj, **kwargs)

    return wrapper


@pytest.fixture
def env():
    """Provides a fresh SimPy environment for each test."""
    return simpy.Environment()
