from __future__ import annotations


FaultType = str
MachineID = int
JobTypeName = str
RngKey = tuple[MachineID, JobTypeName]

Severity = int
Deadline = float
WorkDuration = float
JobID = int
JobPriority = tuple[Severity, Deadline, WorkDuration, JobID]
