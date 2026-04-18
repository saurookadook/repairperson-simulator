from .base import Details, Event
from .machine_events import OnMachineBrokenEvent, OnMachineBrokenEventDetails
from .job_events import (
    OnJobAssignedEvent,
    OnJobAssignedEventDetails,
    OnJobCompletedEvent,
    OnJobCompletedEventDetails,
    OnJobQueuedEvent,
    OnJobQueuedEventDetails,
)

__all__ = [
    "Details",
    "Event",
    "OnMachineBrokenEvent",
    "OnMachineBrokenEventDetails",
    "OnJobAssignedEvent",
    "OnJobAssignedEventDetails",
    "OnJobCompletedEvent",
    "OnJobCompletedEventDetails",
    "OnJobQueuedEvent",
    "OnJobQueuedEventDetails",
]
