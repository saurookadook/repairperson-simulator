from __future__ import annotations

import simpy

from repairperson_simulator_app.simulator.config import RootConfig
from repairperson_simulator_app.simulator.event_logger import EventLogger
from repairperson_simulator_app.simulator.job_manager import JobManager
from repairperson_simulator_app.simulator.machine import Machine
from repairperson_simulator_app.utils.decorators import exceptions_guard


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
        self.working_processes = []

    def start_machines(self):
        for machine in self.machines:
            self.register(machine.start_work())

    def register(self, working_process):
        """Register a machine's 'working' process to be observed."""
        self.working_processes.append(working_process)

    def notify(self, machine: Machine, status):
        """Notify job manager of a machine status change."""
        pass

    @exceptions_guard(simpy.Interrupt)
    def stop_machines_on_horizon_end(self):
        yield self.env.timeout(self.root_config.horizon_in_minutes)
        for process in self.working_processes:
            process.interrupt()
