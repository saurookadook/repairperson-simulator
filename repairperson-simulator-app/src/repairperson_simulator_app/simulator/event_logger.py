from __future__ import annotations

import simpy

from repairperson_simulator_app.events.base import Event
from repairperson_simulator_app.utils.singleton_meta import SingletonMeta


class EventLogger(metaclass=SingletonMeta):
    def __init__(self, env: simpy.Environment):
        self.env = env
        self.events: list[Event] = []

    def log_event(self, event_type: str, details: dict) -> None:
        event = Event(type=event_type, details=details, timestamp=self.env.now)
        self.events.append(event)

    def get_logged_events(self) -> list[Event]:
        return self.events.copy()
