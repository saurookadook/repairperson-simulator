from __future__ import annotations

from typing import Callable

from repairperson_simulator_app.utils.singleton_meta import SingletonMeta

class EventObserver(metaclass=SingletonMeta):
    """A singleton class to register events, listeners for those events, and
    dispatch events to appropriate listeners.
    """

    def __init__(self):
        self._registered_events = {}

    def register_event(self, event_name: str):
        """Register a new event by name."""
        if event_name not in self._registered_events:
            self._registered_events[event_name] = []

    def add_event_listener(self, event_name: str, listener: Callable):
        """Add a new listener (callback function) for a specific event.

        If the event hasn't been registered yet, it will be registered first.
        """
        self.register_event(event_name)
        self._registered_events[event_name].append(listener)

    def dispatch_event(self, event_name: str, *args, **kwargs):
        """Dispatch an event to all registered listeners."""
        if event_name in self._registered_events:
            for listener in self._registered_events[event_name]:
                listener(*args, **kwargs)

    def reset_all_registered_events(self):
        """Reset all registered listeners for all events."""
        self._registered_events = {}


