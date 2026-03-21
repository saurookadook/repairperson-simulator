from __future__ import annotations

import logging
import simpy
from typing import TYPE_CHECKING

from repairperson_simulator_app.constants.enums import JobType
from repairperson_simulator_app.constants.events import (
    EventType,
    MachineLifecycleEventType,
)
from repairperson_simulator_app.simulator.event_logger import EventLogger
from repairperson_simulator_app.events.machine_events import (
    OnMachineBrokenEvent,
    OnMachineBrokenEventDetails,
)
from repairperson_simulator_app.simulator.exceptions import MachineBrokenException
from repairperson_simulator_app.simulator.randomizer import Randomizer
from repairperson_simulator_app.utils.event_observer import event_observer

if TYPE_CHECKING:
    from repairperson_simulator_app.constants.types import FaultType, SystemID
    from repairperson_simulator_app.simulator.config import RootConfig


logger: logging.Logger = logging.getLogger(__name__)


class Machine:
    """A machine produces parts and may get broken every now and then.

    If it breaks, it requests a *repairperson* and continues the production
    after the it is repaired.

    A machine has a *name* and a number of *parts_made* thus far.
    """

    def __init__(
        self,
        env: simpy.Environment,
        root_config: RootConfig,
        randomizer: Randomizer,
        *,
        id: SystemID,
        name: str,
    ):
        self.env = env
        self.id = id
        self.name = name
        self.randomizer = randomizer
        self.root_config = root_config

        self.event_logger = EventLogger(self.env)
        self.is_broken = False
        self.parts_made = 0
        self._done_in = 0.0

    def start_work(self):
        """Start the machine's operation."""
        self.working_process = self.env.process(self.do_work())
        for fault_type in self.root_config.fault_types_map.keys():
            self.env.process(self.intermittently_break(fault_type))
        return self.working_process

    def do_work(self):
        """Produce parts as long as the simulation runs.

        While making a part, the machine may break multiple times.
        Request a repairperson when this happens.

        """
        self.event_logger.log_event(
            details=dict(
                machine_id=self.id,
                machine_name=self.name,
                parts_made=self.parts_made,
            ),
            event_type=MachineLifecycleEventType.MACHINE_WORK_STARTED.value,
        )

        while True:
            self._done_in = self.randomizer.time_per_part()
            while self._done_in:
                start = self.env.now
                try:
                    yield self.env.timeout(self._done_in)
                    self._done_in = 0  # Set to 0 to exit while loop.

                except simpy.Interrupt as exc:
                    self._done_in -= self.env.now - start
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
                    return
                    # raise MachineBrokenException(self.name, self.env.now) from exc
                    # done_in -= self.env.now - start

                    # with repairperson.request(priority=1) as req:
                    #     yield req
                    #     # TODO: get job details and pass "remaining_duration"
                    #     yield self.env.timeout()

                    # self.is_broken = False

            self.parts_made += 1
            self.event_logger.log_event(
                details=dict(
                    machine_id=self.id,
                    machine_name=self.name,
                    parts_made=self.parts_made,
                ),
                event_type=MachineLifecycleEventType.MACHINE_COMPLETED_PART.value,
            )

    def intermittently_break(self, fault_type: FaultType):
        """Break the machine at random intervals."""
        while True:
            time_until_failure = (
                self.randomizer.time_to_failure_in_minutes_for_system_and_fault_type(
                    self.id, fault_type
                )
            )
            logger.debug(
                f"Machine '{self.name}' will break in {time_until_failure:.2f} minutes. ({time_until_failure*60:.2f} seconds)"
            )
            yield self.env.timeout(time_until_failure)
            if not self.is_broken:
                logger.debug(
                    f"Machine '{self.name}' broken at {self.env.now} seconds. ({self.env.now/60:.2f} minutes)"
                )
                self.working_process.interrupt()
