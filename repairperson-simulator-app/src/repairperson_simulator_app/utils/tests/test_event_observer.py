from __future__ import annotations

import pytest

from repairperson_simulator_app.utils.event_observer import EventObserver


ON_DECREMENT_COUNT = "on_decrement_count"
ON_INCREMENT_COUNT = "on_increment_count"
ON_MACHINE_BROKEN = "on_machine_broken"


@pytest.fixture
def event_observer():
    instance = EventObserver()
    instance._registered_events = {}
    return instance


def test_event_observer_register_event_new_event(event_observer):
    event_observer.register_event(ON_MACHINE_BROKEN)

    assert ON_MACHINE_BROKEN in event_observer._registered_events
    assert event_observer._registered_events[ON_MACHINE_BROKEN] == []


def test_event_observer_register_event_existing_event(event_observer):
    event_observer.register_event(ON_MACHINE_BROKEN)

    assert ON_MACHINE_BROKEN in event_observer._registered_events
    assert event_observer._registered_events[ON_MACHINE_BROKEN] == []

    event_observer._registered_events[ON_MACHINE_BROKEN].append(lambda: None)
    event_observer.register_event(ON_MACHINE_BROKEN)
    assert len(event_observer._registered_events[ON_MACHINE_BROKEN]) == 1


def test_event_observer_add_event_listener(event_observer):
    event_observer.add_event_listener(ON_MACHINE_BROKEN, lambda: "listener1")
    event_observer.add_event_listener(ON_MACHINE_BROKEN, lambda: "listener2")

    assert ON_MACHINE_BROKEN in event_observer._registered_events
    assert len(event_observer._registered_events[ON_MACHINE_BROKEN]) == 2
    assert all(callable(listener) for listener in event_observer._registered_events[ON_MACHINE_BROKEN])


def test_event_observer_dispatch_event_multiple_listeners(event_observer):
    count = 0

    def plus_one():
        nonlocal count
        count += 1

    def plus_two():
        nonlocal count
        count += 2

    event_observer.add_event_listener(ON_INCREMENT_COUNT, plus_one)
    event_observer.add_event_listener(ON_INCREMENT_COUNT, plus_one)
    event_observer.add_event_listener(ON_INCREMENT_COUNT, plus_two)

    event_observer.dispatch_event(ON_INCREMENT_COUNT)
    assert count == 4


def test_event_observer_dispatch_event_does_not_call_listeners_for_other_registered_events(event_observer):
    count = 0

    def plus_one():
        nonlocal count
        count += 1

    def minus_one():
        nonlocal count
        count -= 1

    event_observer.add_event_listener(ON_INCREMENT_COUNT, plus_one)
    event_observer.add_event_listener(ON_DECREMENT_COUNT, minus_one)

    event_observer.dispatch_event(ON_DECREMENT_COUNT)
    assert count == -1

    event_observer.dispatch_event(ON_INCREMENT_COUNT)
    assert count == 0


def test_event_observer_reset_all_registered_events(event_observer):
    event_observer.add_event_listener(ON_DECREMENT_COUNT, lambda: None)
    event_observer.add_event_listener(ON_INCREMENT_COUNT, lambda: None)
    event_observer.add_event_listener(ON_INCREMENT_COUNT, lambda: None)
    event_observer.add_event_listener(ON_MACHINE_BROKEN, lambda: None)

    assert len(event_observer._registered_events.keys()) == 3
    assert len(event_observer._registered_events[ON_DECREMENT_COUNT]) == 1
    assert len(event_observer._registered_events[ON_INCREMENT_COUNT]) == 2
    assert len(event_observer._registered_events[ON_MACHINE_BROKEN]) == 1

    event_observer.reset_all_registered_events()
    assert event_observer._registered_events == {}



