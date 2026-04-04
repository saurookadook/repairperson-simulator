from __future__ import annotations

import logging
import pytest


local_logger: logging.Logger = logging.getLogger(__name__)


@pytest.mark.preemption
def test_operator_manager_handles_preemption_for_different_machines():
    """
    Tests that the operator manager correctly handles job preemption based on priority.
    """
    pass


@pytest.mark.preemption
def test_operator_manager_handles_preemption_exits_at_horizon():
    """
    Tests that the operator manager correctly handles job preemption based on
    priority but exits at the simulation horizon.
    """
    pass


@pytest.mark.preemption
def test_operator_manager_handles_preemption_for_multiple_operators():
    """
    Tests that the operator manager correctly handles job preemption based on priority
    for multiple operators across multiple machines.

    Tests following scenarios:
    - Free operators are prioritized during job assignment over busy operators.
    - Busy operators are preempted when no free operators are available AND when
        their current job is lower priority than the incoming job.
    - Busy operators are NOT preempted when their current job is higher priority
        than the incoming job.
    - Operators resume preempted jobs after completing higher priority jobs.
    """
    pass


@pytest.mark.preemption
def test_operator_manager_handles_preemption_TBD():
    pass
