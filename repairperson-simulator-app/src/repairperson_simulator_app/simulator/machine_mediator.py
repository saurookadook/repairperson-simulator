from __future__ import annotations

import simpy
from dataclasses import dataclass, field

from repairperson_simulator_app.constants import HORIZON_END
from repairperson_simulator_app.simulator.config import RootConfig
from repairperson_simulator_app.simulator.event_logger import EventLogger
from repairperson_simulator_app.simulator.job_manager import JobManager
from repairperson_simulator_app.simulator.machine import Machine
from repairperson_simulator_app.utils.decorators import exceptions_guard


@dataclass
class RegistryEntry:
    fault_processes: list[simpy.Process] = field(default_factory=list)
    working_process: simpy.Process | None = None

    def update(
        self, fault_processes: list[simpy.Process], working_process: simpy.Process
    ):
        self.fault_processes = fault_processes
        self.working_process = working_process


class MachineMediator:
    """Mediator for monitoring machine status changes."""

    def __init__(
        self,
        env: simpy.Environment,
        root_config: RootConfig,
        job_manager: JobManager,
        machines: list[Machine],
    ):
        self.env = env
        self.root_config = root_config
        self.job_manager = job_manager
        self.machines = machines

        self.event_logger = EventLogger(self.env)
        self.working_processes: list[simpy.Process] = []
        self.machine_registry = {
            machine.id: RegistryEntry() for machine in self.machines
        }
        self.stop_machines_process = self.env.process(
            self.stop_machines_on_horizon_end()
        )

    def start_all_machines(self):
        for machine in self.machines:
            m = machine.start_work()
            self.register(m)

    def register(self, machine: Machine):
        """Register a machine's 'working' process to be observed."""
        self.machine_registry[machine.id].update(
            machine.fault_processes,
            machine.working_process,
        )

    def notify(self, machine: Machine, status):
        """Notify job manager of a machine status change."""
        pass

    @exceptions_guard(simpy.Interrupt)
    def stop_machines_on_horizon_end(self):
        yield self.env.timeout(self.root_config.horizon_in_minutes)

        for machine in self.machines:
            machine.cleanup_at_horizon_end()
