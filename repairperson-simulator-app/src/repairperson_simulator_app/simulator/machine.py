from __future__ import annotations

import logging
import simpy
from typing import TYPE_CHECKING

from repairperson_simulator_app.constants import (
    HORIZON_END,
    EventType,
    MachineLifecycleEventType,
    MachineStatus,
)
from repairperson_simulator_app.events.machine_events import OnMachineBrokenEventDetails
from repairperson_simulator_app.simulator.event_logger import EventLogger
from repairperson_simulator_app.events.machine_events import OnMachineBrokenEventDetails
from repairperson_simulator_app.simulator.exceptions import HorizonReached
from repairperson_simulator_app.simulator.randomizer import Randomizer
from repairperson_simulator_app.utils.decorators import horizon_guard
from repairperson_simulator_app.utils.event_observer import event_observer

if TYPE_CHECKING:
    from repairperson_simulator_app.constants.types import FaultType, MachineID
    from repairperson_simulator_app.simulator.config import RootConfig

# TODO: delete me later :D
from rich import inspect as ri
from rich.pretty import pretty_repr as pr


class Machine:
    """A machine produces parts and may get broken every now and then.

    If it breaks, it requests a *repairperson* and continues the production
    after the it is repaired.

    A machine has a *name* and a number of *parts_made* thus far.
    """

    working_process: simpy.Process

    def __init__(
        self,
        env: simpy.Environment,
        root_config: RootConfig,
        randomizer: Randomizer,
        *,
        id: MachineID,
        name: str,
    ):
        self.env = env
        self.id = id
        self.name = name
        self.randomizer = randomizer
        self.root_config = root_config

        self.logger: logging.Logger = logging.getLogger(f"{__name__}.Machine-{id}")

        self.event_logger = EventLogger(self.env)
        self.status: MachineStatus = MachineStatus.IDLE
        self.wait_on_repair: simpy.Event | None = None
        self.parts_made = 0
        self._done_in = 0.0

        self.fault_processes: list[simpy.Process] = []

    def start_work(self) -> Machine:
        """Start the machine's operation."""
        self.working_process = self.env.process(self.do_work())

        for fault_type in self.root_config.fault_types_map.keys():
            fault_process = self.env.process(self.intermittently_break(fault_type))
            self.fault_processes.append(fault_process)

        return self

    def cleanup_at_horizon_end(self):
        self.logger.debug(
            f"Cleaning up machine '{self.name}' processes at horizon end."
        )
        try:
            self.logger.debug(f"Interrupting working process of machine '{self.name}'.")
            self.working_process.interrupt(HORIZON_END)
        except Exception:
            pass

        for i, process in enumerate(self.fault_processes):
            try:
                self.logger.debug(
                    f"Interrupting fault process {i} of machine '{self.name}'."
                )
                process.interrupt(HORIZON_END)
            except Exception:
                pass

    @horizon_guard
    def do_work(self):
        """Produce parts as long as the simulation runs.

        While making a part, the machine may break multiple times.
        Request a repairperson when this happens.

        """
        wrk_start_kwargs = dict(
            event_type=MachineLifecycleEventType.MACHINE_WORK_STARTED.value,
            details=dict(
                machine_id=self.id,
                machine_name=self.name,
                parts_made=self.parts_made,
            ),
        )
        self.logger.debug(pr(wrk_start_kwargs))
        self.event_logger.log_event(**wrk_start_kwargs)  # type: ignore

        while True:
            self._done_in = self.randomizer.time_per_part(self.id)

            while self._done_in > 0:
                start = self.env.now
                self.status = MachineStatus.WORKING

                try:
                    yield self.env.timeout(self._done_in)
                    self._done_in = 0  # Set to 0 to exit while loop.

                except simpy.Interrupt as exc:
                    if HORIZON_END in str(exc.cause):
                        raise HorizonReached()

                    fault_type = str(exc.cause)
                    fault_type_cfg = self.root_config.fault_types_map[fault_type]

                    self.status = MachineStatus.BROKEN
                    self._done_in -= self.env.now - start
                    self.wait_on_repair = self.env.event()

                    job_type = fault_type_cfg.job_type
                    repair_time = fault_type_cfg.sample_repair_time_in_minutes()

                    evt_kwargs = dict(
                        event_type=EventType.ON_MACHINE_BROKEN.value,
                        details=OnMachineBrokenEventDetails(
                            machine=self,
                            job_type=job_type,
                            repair_time_in_min=repair_time,
                        ),
                    )

                    self.logger.debug(pr(evt_kwargs))
                    self.event_logger.log_event(**evt_kwargs)  # type: ignore
                    event_observer.dispatch_event(**evt_kwargs)  # type: ignore

                    self.logger.debug(
                        f"\n{'?'*160}"
                        f"\nMachine '{self.name}' is waiting for repair..."
                        f"\n{'?'*160}"
                    )
                    yield self.wait_on_repair

                    self.status = MachineStatus.IDLE
                    self.wait_on_repair = None
                    self.logger.debug(
                        f"Machine '{self.name}' repaired and back to idle at {self.env.now} seconds."
                    )
                    break

            self.parts_made += 1
            self.event_logger.log_event(
                details=dict(
                    machine_id=self.id,
                    machine_name=self.name,
                    parts_made=self.parts_made,
                ),
                event_type=MachineLifecycleEventType.MACHINE_COMPLETED_PART.value,
            )

    @horizon_guard
    def intermittently_break(self, fault_type: FaultType):
        """Break the machine at random intervals."""
        while True:
            time_until_failure = (
                self.randomizer.time_to_failure_in_minutes_for_machine_and_fault_type(
                    self.id, fault_type
                )
            )

            # self.logger.debug(
            #     f"Machine '{self.name}' will break in {time_until_failure:.2f} minutes. ({time_until_failure*60:.2f} seconds)"
            # )
            yield self.env.timeout(time_until_failure)

            if self.status == MachineStatus.BROKEN:
                continue

            self.logger.debug(
                f"Machine '{self.name}' broken at {self.env.now} seconds. ({self.env.now/60:.2f} minutes)"
            )
            self.working_process.interrupt(fault_type)

    def _waiting_on_repair(self) -> bool:
        return isinstance(self.wait_on_repair, simpy.Event)
