from __future__ import annotations

import simpy
from simpy.resources.store import StoreGet, StorePut
from typing import Any, Callable

from repairperson_simulator_app.simulator.entities import Operator
from repairperson_simulator_app.simulator.interfaces import AbstractBaseStore


class OperatorFilterStore(AbstractBaseStore):
    """A custom SimPy store that allows for filtering operators based on criteria."""

    def __init__(self, env: simpy.Environment):
        self.env = env
        self.store = simpy.FilterStore(env)

    def get(self, filter_func: Callable[[Operator], bool]) -> StoreGet:
        """Get an operator from the store that matches the filter function."""
        return self.store.get(filter_func)

    def get_by_id_from_store(self, operator_id: int) -> StoreGet:
        return self.get(lambda op: op.id == operator_id)

    def put(self, operator: Operator) -> StorePut:
        """Put an operator into the store."""
        return self.store.put(operator)

    @property
    def items(self) -> list[Operator]:
        return self.store.items

    def size(self) -> int:
        return len(self.store.items)
