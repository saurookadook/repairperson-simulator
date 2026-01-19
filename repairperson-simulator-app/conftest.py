import logging
import pytest
from rich import inspect

from repairperson_simulator_app.utils.logging import configure_logging

test_logger = configure_logging("TEST_LOGGER")


@pytest.fixture(scope="session")
def rich_inspect():
    def wrapper(obj, **kwargs):
        return inspect(obj, **kwargs)

    return wrapper
    # """A fixture that exposes `rich.inspect` inside all tests for easy debugging."""
    # return inspect
    # """A fixture that provides a rich inspect function for debugging."""
    # return lambda obj: inspect(obj, console=configure_logging("TEST_LOGGER").handlers[0].console)
