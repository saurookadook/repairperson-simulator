from __future__ import annotations

import simpy


class JobPriorityStore:
    """A custom SimPy store that allows for priority-based retrieval of jobs."""

    def __init__(self, env: simpy.Environment):
        self.env = env
        self.store = simpy.PriorityStore(env)

    def get(self):
        """Get the highest priority job from the store."""
        return self.store.get()

    def put(self, job):
        """Put a job into the store with its priority."""
        self.store.put(simpy.PriorityItem(job.priority, job))
