from __future__ import annotations

from repairperson_simulator_app.simulator.machine import Machine

Severity = int
Deadline = float
WorkDuration = float
JobID = int
JobPriority = tuple[Severity, Deadline, WorkDuration, JobID]
