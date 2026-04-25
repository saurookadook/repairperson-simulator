from __future__ import annotations

import logging
import simpy
from copy import deepcopy
from simpy.resources.store import StoreGet, StorePut
from typing import Any, Callable

from repairperson_simulator_app.simulator.config import EngineConfig
from repairperson_simulator_app.simulator.entities import Job, Operator
from repairperson_simulator_app.simulator.event_logger import EventLogger
from repairperson_simulator_app.simulator.interfaces import AbstractBaseStore

# TODO: delete me later :D
from rich import inspect as ri
from rich.pretty import pretty_repr as pr


class OperatorFilterStore(AbstractBaseStore):
    """A custom SimPy store that allows for filtering operators based on criteria."""

    def __init__(self, env: simpy.Environment, engine_config: EngineConfig):
        self.env = env
        self.engine_config = engine_config
        self.store = simpy.FilterStore(env)

        self.logger: logging.Logger = logging.getLogger(self.__class__.__name__)

        self.event_logger = EventLogger(self.env)
        # TODO: maybe deep copy?
        self.operators: list[Operator] = engine_config.operators
        # NOTE: creating separate list of operators as mutating `store.items` will
        # mutate references in `self.operators`
        self.store.items = [deepcopy(op) for op in self.engine_config.operators]

    def get(self, filter_func: Callable[[Operator], bool]) -> StoreGet:
        """Get an operator from the store that matches the filter function."""
        return self.store.get(filter_func)

    def get_by_id_from_store(self, operator_id: int) -> StoreGet:
        return self.get(lambda op: op.id == operator_id)

    def get_first_available_for_job(self, job: Job) -> StoreGet | None:
        self.logger.debug(
            f"    Getting first available operator for job '{job.id}'    ".center(
                180, "*"
            )
        )
        self.logger.debug(f"operator store size: {self.size()}")
        if self.size() == 0:
            return None

        available_ops = self._find_available_operators_for_job(job)
        if len(available_ops) == 0:
            return None
        return self.get_by_id_from_store(available_ops[0].id)

    def get_available_operators_for_job(self, job: Job) -> list[Operator]:
        return self._find_available_operators_for_job(job)

    def get_other_available_operators_for_job(
        self, job: Job, excludable_operator: Operator
    ) -> list[Operator]:
        return self._find_other_available_operators_for_job(job, excludable_operator)

    def update_operator(self, operator_id: int, **kwargs) -> Operator:
        operator = self.get_operator_by_id(operator_id)
        for key, value in kwargs.items():
            setattr(operator, key, value)
        return operator

    def update_operator_for_arrival_at_machine(
        self, operator_id: int, machine_id: int
    ) -> Operator:
        operator = self.get_operator_by_id(operator_id)
        operator.update_for_arrival_at_machine(machine_id)
        return operator

    def update_operator_for_job_start(self, operator_id: int, job: Job) -> Operator:
        operator = self.get_operator_by_id(operator_id)
        operator.update_for_job_start(job)
        return operator

    def update_operator_for_job_complete(self, operator_id: int) -> Operator:
        operator = self.get_operator_by_id(operator_id)
        operator.update_for_job_complete()
        return operator

    def update_operator_for_preemption(self, operator_id: int) -> Operator:
        operator = self.update_operator_for_job_complete(operator_id)
        operator.in_transit = False
        return operator

    def update_operator_on_return_to_resting_location(
        self, operator_id: int, machine_id: int
    ) -> Operator:
        # TODO: implement later
        operator = self.get_operator_by_id(operator_id)
        operator.machine_location = machine_id
        return operator

    def _find_available_operators_for_job(self, job: Job) -> list[Operator]:
        available_operators: list[Operator] = []

        job_prio = job.priority

        for operator in self.store.items:
            op_job_prio = operator.current_job_priority

            self.logger.debug(
                pr(
                    dict(
                        job_priority=job_prio,
                        operator_id=operator.id,
                        operator_name=operator.name,
                        operator_current_job_priority=op_job_prio,
                        operator_is_available_for_job=operator.is_available_for_job(
                            job
                        ),
                    )
                )
            )
            if operator.is_available_for_job(job) or (
                job_prio is not None
                and op_job_prio is not None
                and job_prio[:3] < op_job_prio[:3]
            ):
                available_operators.append(operator)

        available_operators.sort(
            key=lambda op: (
                op.get_distance_to_machine(job.machine_id),
                op.id,
            )
        )
        return available_operators

    def _find_other_available_operators_for_job(
        self, job: Job, excludable_operator: Operator
    ) -> list[Operator]:
        available_operators = []
        for operator in self.store.items:
            if operator.id != excludable_operator.id and operator.is_available_for_job(
                job
            ):
                available_operators.append(operator)
        return available_operators

    def put(self, operator: Operator) -> StorePut:
        """Put an operator into the store."""
        self.operators[operator.id] = operator
        if any(op.id == operator.id for op in self.store.items):
            self.get_by_id_from_store(operator.id)
        self.logger.debug(f"Operator '{operator.id}' put into store.")
        return self.store.put(operator)

    @property
    def items(self) -> list[Operator]:
        return self.store.items

    def size(self) -> int:
        return len(self.store.items)

    def get_operator_by_id(self, operator_id: int) -> Operator:
        """
        Gets an ``Operator`` by ID directly from ``self.operators`` list, not from the store.
        """
        return self.operators[operator_id]
