from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime as dtime
from typing import Callable, Optional

from repairperson_simulator_app.events.base import Event
from repairperson_simulator_app.utils.singleton_meta import SingletonMeta


ListenerCallback = Callable[[Event], None]


class EventObserver(metaclass=SingletonMeta):
    """A singleton class to register events, listeners for those events, and
    dispatch events to appropriate listeners.
    """

    def __init__(self):
        self._registered_events = {}

    def register_event(self, event_type: str):
        """Register a new event by name."""
        if event_type not in self._registered_events:
            self._registered_events[event_type] = []

    def add_event_listener(self, event_type: str, listener: ListenerCallback):
        """Add a new listener (callback function) for a specific event.

        If the event hasn't been registered yet, it will be registered first.
        """
        self.register_event(event_type)
        self._registered_events[event_type].append(listener)

    def dispatch_event(self, event_type: str, details: Optional[dict] = None):
        """Dispatch an event to all registered listeners."""
        if event_type in self._registered_events:
            event = Event(
                type=event_type,
                timestamp=dtime.now().timestamp(),
                details=details,
            )
            for listener in self._registered_events[event_type]:
                listener(event)

    def reset_all_registered_events(self):
        """Reset all registered listeners for all events."""
        self._registered_events = {}
