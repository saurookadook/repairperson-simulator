#!/usr/bin/env python3

from __future__ import annotations

import logging
import simpy
from csv import DictWriter
from datetime import datetime
from rich import inspect

from repairperson_simulator_app.events.base import Event
from repairperson_simulator_app.simulator.config import EngineConfig, RootConfig
from repairperson_simulator_app.simulator.entities import Operator
from repairperson_simulator_app.simulator.event_logger import EventLogger
from repairperson_simulator_app.simulator.job_manager import JobManager
from repairperson_simulator_app.simulator.job_priority_store import JobPriorityStore
from repairperson_simulator_app.simulator.machine import Machine
from repairperson_simulator_app.simulator.machine_mediator import MachineMediator
from repairperson_simulator_app.simulator.operator_filter_store import (
    OperatorFilterStore,
)
from repairperson_simulator_app.simulator.operator_manager import OperatorManager
from repairperson_simulator_app.simulator.randomizer import Randomizer
from repairperson_simulator_app.utils.filesystem import get_project_root
from repairperson_simulator_app.utils.logging import configure_logging

try:
    import shutil

    raw_window_with, _ = shutil.get_terminal_size()
except OSError:
    raw_window_with = 200

window_width = (
    raw_window_with - 160
)  # To account for characters added by logging handlers


root_logger: logging.Logger = configure_logging()

project_root_path = get_project_root(__file__)


def create_engine_config(
    env: simpy.Environment, root_config: RootConfig
) -> EngineConfig:
    machines = [
        Machine(
            env=env,
            root_config=root_config,
            id=i,
            name=f"Machine {i}",
            randomizer=Randomizer(root_config=root_config),
        )
        for i in range(root_config.machine_config.count)
    ]
    operators = [
        Operator(
            id=i,
            name=f"Operator {i}",
            walk_rate=root_config.operator_config.walk_rate,
        )
        for i in range(root_config.operator_config.count)
    ]

    return EngineConfig(
        horizon_in_minutes=root_config.horizon_in_minutes,
        machines=machines,
        operators=operators,
    )


class SimEngine:
    def __init__(
        self,
        env: simpy.Environment,
        root_config: RootConfig,
    ):
        self.env = env
        self.root_config = root_config

        self.engine_config: EngineConfig = create_engine_config(env, root_config)
        self.event_logger: EventLogger = EventLogger(self.env)
        self.job_store: JobPriorityStore = JobPriorityStore(self.env)
        self.job_manager: JobManager = JobManager(
            self.env, self.engine_config, self.job_store
        )
        self.machine_mediator: MachineMediator = MachineMediator(
            self.env, self.root_config, self.job_manager, self.engine_config.machines
        )
        self.operator_filter_store: OperatorFilterStore = OperatorFilterStore(
            self.env, self.engine_config
        )
        self.operator_manager: OperatorManager = OperatorManager(
            self.env,
            self.engine_config,
            self.root_config,
            self.job_manager,
            self.machine_mediator,
            self.operator_filter_store,
        )

    def get_logs(self) -> list[Event]:
        return self.event_logger.get_logged_events()

    def start_simulation(self):
        self.job_manager.setup_listeners()
        self.operator_manager.setup_listeners()
        self.machine_mediator.start_all_machines()

        self.env.run(until=self.engine_config.horizon_in_minutes)


def create_csv_log_row(event: Event):
    evt_details = getattr(event, "details", {})
    return dict(
        event_type=evt_details.get("event_type"),
        timestamp=evt_details.get("timestamp"),
        job_type=evt_details.get("job_type"),
    )


def run_simulation(
    root_config: RootConfig, env: simpy.Environment = simpy.Environment()
):
    engine = SimEngine(env, root_config)
    engine.start_simulation()

    logs = engine.get_logs()

    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = (
        project_root_path
        / "data"
        / "simulation_runs"
        / f"simulation_run_logs_{timestamp_str}.csv"
    )
    with output_file.open("w", newline="") as csvfile:
        fieldnames_set = set()
        csv_rows = []

        for log in logs:
            row = log.get_csv_row()
            # inspect((log, row))
            # breakpoint()
            csv_rows.append(row)

            fieldnames_set.update(row.keys())

        fieldnames_set.discard("event_type")
        fieldnames_set.discard("timestamp")

        fieldnames = ["event_type", "timestamp"] + sorted(fieldnames_set)
        inspect(fieldnames, title="CSV Fieldnames")
        writer = DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for i, row in enumerate(csv_rows, start=1):
            log_msg = f"Writing row to CSV :: #{i} - event_type='{row.get('event_type')}' | timestamp={row.get('timestamp')}"

            root_logger.info(log_msg)
            writer.writerow(row)


def parse_and_create_root_config():
    pass


def simulator_main():
    # # parse config from some file
    # root_config = parse_and_create_root_config()
    from repairperson_simulator_app.test_factories.config import RootConfigFactory

    root_config = RootConfigFactory()
    root_config.horizon_in_minutes = 60 * 24 * 7
    root_config.operator_config.count = 1
    run_simulation(root_config)  # type: ignore - TMP


if __name__ == "__main__":
    root_logger.setLevel(logging.WARNING)
    print(f"Logging Level: {root_logger.getEffectiveLevel()}")
    simulator_main()
