from __future__ import annotations

import simpy
from copy import copy
from heapq import heapify, heappop
from simpy.resources.store import StoreGet, StorePut
from typing import Any

from repairperson_simulator_app.simulator.entities import Job
from repairperson_simulator_app.simulator.interfaces import AbstractBaseStore


class JobPriorityStore(AbstractBaseStore):
    """A custom SimPy store that allows for priority-based retrieval of jobs."""

    def __init__(self, env: simpy.Environment):
        self.env = env
        self.store = simpy.PriorityStore(env)

    @property
    def items(self) -> list[Any]:
        return self.store.items

    def get(self) -> StoreGet:
        """Get the highest priority job from the store."""
        return self.store.get()

    def put(self, job: Job) -> StorePut:
        """Put a job into the store with its priority."""
        return self.store.put(simpy.PriorityItem(job.priority, job))

    def clear_items(self) -> None:
        self.store.items.clear()

    def size(self) -> int:
        return len(self.store.items)

    def __contains__(self, target_job: Job):
        job_items_heap = copy(self.store.items)
        heapify(job_items_heap)

        while len(job_items_heap) > 0:
            _, job = heappop(job_items_heap)

            if target_job.id == job.id:
                return True

        return False
