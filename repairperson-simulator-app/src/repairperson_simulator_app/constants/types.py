from __future__ import annotations


SystemID = int
FaultType = str
RngKey = tuple[SystemID, FaultType]

Severity = int
Deadline = float
WorkDuration = float
JobID = int
JobPriority = tuple[Severity, Deadline, WorkDuration, JobID]
