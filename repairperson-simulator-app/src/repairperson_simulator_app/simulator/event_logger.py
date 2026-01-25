from __future__ import annotations

import simpy
from typing import Dict


class EventLogger:
    def __init__(self, env: simpy.Environment):
        self.env = env
        self.events = []

    def log_event(self, event_type: str, details: Dict):
        event = {
            "details": details,
            "event_type": event_type,
            "timestamp_in_seconds": self.env.now,
        }
        self.events.append(event)

    def get_logged_events(self):
        return self.events.copy()
