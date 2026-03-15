from __future__ import annotations

import logging
import simpy

from repairperson_simulator_app.constants.enums import JobType
from repairperson_simulator_app.constants.events import EventType
from repairperson_simulator_app.simulator.entities import Operator
from repairperson_simulator_app.events.machine_events import (
    OnMachineBrokenEvent,
    OnMachineBrokenEventDetails,
)
from repairperson_simulator_app.simulator.exceptions import MachineBrokenException
from repairperson_simulator_app.simulator.randomizer import Randomizer
from repairperson_simulator_app.utils.event_observer import event_observer

logger: logging.Logger = logging.getLogger(__name__)


class Machine:
    """A machine produces parts and may get broken every now and then.

    If it breaks, it requests a *repairperson* and continues the production
    after the it is repaired.

    A machine has a *name* and a number of *parts_made* thus far.
    """

    def __init__(
        self, env: simpy.Environment, id: int, name: str, randomizer: Randomizer
    ):
        self.env = env
        self.id = id
        self.name = name
        self.is_broken = False
        self.parts_made = 0
        self.randomizer = randomizer

    def start_work(self, repairperson: Operator):
        """Start the machine's operation."""
        self.working_process = self.env.process(self.working(repairperson))
        self.env.process(self.intermittently_break())

    def working(self, repairperson: Operator):
        """Produce parts as long as the simulation runs.

        While making a part, the machine may break multiple times.
        Request a repairperson when this happens.

        """
        while True:
            done_in = self.randomizer.time_per_part()
            while done_in:
                start = self.env.now
                try:
                    yield self.env.timeout(done_in)
                    done_in = 0  # Set to 0 to exit while loop.

                except simpy.Interrupt as exc:
                    self.is_broken = True
                    # TODO: this should be semi-randomized
                    job_type = JobType.MECHANICAL_REPAIR
                    # TODO: this should be semi-randomized and/or dependent on job type
                    repair_time_in_min = 20.0
                    event_observer.dispatch_event(
                        EventType.ON_MACHINE_BROKEN.value,
                        details=OnMachineBrokenEventDetails(
                            machine=self,
                            job_type=job_type,
                            repair_time_in_min=repair_time_in_min,
                        ),
                    )
                    # raise MachineBrokenException(self.name, self.env.now) from exc
                    # done_in -= self.env.now - start

                    # with repairperson.request(priority=1) as req:
                    #     yield req
                    #     # TODO: get job details and pass "remaining_duration"
                    #     yield self.env.timeout()

                    # self.is_broken = False

            self.parts_made += 1

    def intermittently_break(self):
        """Break the machine at random intervals."""
        while True:
            time_until_failure = self.randomizer.time_to_failure_in_seconds()
            logger.debug(
                f"Machine '{self.name}' will break in {time_until_failure:.2f} seconds. ({time_until_failure/60:.2f} minutes)"
            )
            yield self.env.timeout(time_until_failure)
            if not self.is_broken:
                logger.debug(
                    f"Machine '{self.name}' broken at {self.env.now} seconds. ({self.env.now/60:.2f} minutes)"
                )
                self.working_process.interrupt()
