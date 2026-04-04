from __future__ import annotations

import logging
import pytest


local_logger: logging.Logger = logging.getLogger(__name__)


@pytest.mark.resting_location
def test_operator_manager_correctly_assigns_initial_resting_locations():
    pass


@pytest.mark.resting_location
def test_operator_manager_operators_return_to_resting_location_when_not_busy():
    pass


@pytest.mark.preemption
@pytest.mark.resting_location
def test_operator_manager_operators_are_preemptible_while_returning_to_resting_location():
    pass


@pytest.mark.preemption
@pytest.mark.resting_location
def test_operator_manager_assigns_operators_to_jobs_based_on_resting_location():
    """
    Emulated series of events:
    - simulation starts with:
        * 5 machines
        * 2 operators
            - `operator 0` has ``resting_location`` at `machine 3`
            - `operator 1` has ``resting_location`` at `machine 1`
    - a mid priority job for `machine 0` arrives => `operator 1` is preempted from `machine 1` and
        assigned to `machine 0` (since it's closer to `operator 0` at `machine 3`)
    - a mid priority job for `machine 2` arrives => `operator 0` is preempted from `machine 3` and
        assigned to `machine 2` (since it's equidistant but `operator 0` has a lower priority
        job than `operator 1`)
    - a high priority job arrives for `machine 4` arrives => `operator 0` is preempted from `machine 2` and
        assigned to `machine 4` (since it's closer than `operator 1` at `machine 0`)
    - `operator 1` completes job at `machine 0` and is assigned to job at `machine 2`
    - `operator 0` completes job at `machine 4` and is assigned to job at `machine 1`
    - `operator 1` starts service at `machine 2`
    - `operator 0` starts service at `machine 1`
    - `operator 1` completes job at `machine 2` and is assigned to job at `machine 3`
    - `operator 1` starts service at `machine 3`
    - `operator 0` completes job at `machine 1`
    - `operator 0` completes job at `machine 3`
    """
