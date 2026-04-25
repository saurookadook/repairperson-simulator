from __future__ import annotations

import pytest
import simpy
from typing import Any, Callable

from repairperson_simulator_app.constants import JobType
from repairperson_simulator_app.simulator.entities import Job
from repairperson_simulator_app.simulator.job_priority_store import JobPriorityStore


@pytest.fixture
def job_factory() -> Callable[..., Job]:
    """Builds jobs with sensible defaults while allowing per-test overrides."""

    def factory(**overrides: Any) -> Job:
        defaults: dict[str, Any] = {
            "created_at_ts": 0.0,
            "id": 1,
            "job_type": JobType.MECHANICAL_REPAIR,
            "machine_id": 1,
            "planned_duration": 30.0,
            "remaining_duration": 30.0,
        }
        merged_dicts = defaults | overrides
        return Job(**merged_dicts)

    return factory


def test_job_priority_store_initialization(env: simpy.Environment):
    store = JobPriorityStore(env)

    assert store.env is env
    assert isinstance(store.store, simpy.PriorityStore)
    assert store.items == []
    assert store.size() == 0


def test_put_stores_priority_item_and_updates_size(
    job_store: JobPriorityStore,
    job_factory: Callable[..., Job],
):
    job = job_factory(id=10)

    put_event = job_store.put(job)

    assert put_event.ok
    assert job_store.size() == 1

    stored_priority_item = job_store.items[0]
    assert stored_priority_item.priority == job.priority
    assert stored_priority_item.item is job


def test_get_yields_highest_priority_job(
    env: simpy.Environment,
    job_store: JobPriorityStore,
    job_factory: Callable[..., Job],
):
    low_priority_job = job_factory(id=3, job_type=JobType.SOFTWARE_UPDATE)
    medium_priority_job = job_factory(id=2, job_type=JobType.MECHANICAL_MAINTENANCE)
    high_priority_job = job_factory(id=1, job_type=JobType.ELECTRICAL_REPAIR)

    job_store.put(low_priority_job)
    job_store.put(medium_priority_job)
    job_store.put(high_priority_job)

    get_event = job_store.get()
    env.run(until=get_event)

    assert get_event.ok
    assert get_event.value.priority == high_priority_job.priority
    assert get_event.value.item is high_priority_job
    assert job_store.size() == 2


def test_get_from_empty_store_waits_until_item_is_available(
    env: simpy.Environment,
    job_store: JobPriorityStore,
    job_factory: Callable[..., Job],
):
    get_event = job_store.get()
    assert not get_event.triggered

    queued_job = job_factory(id=123)
    job_store.put(queued_job)
    env.run(until=get_event)

    assert get_event.triggered
    assert get_event.value.item is queued_job


def test_clear_items_removes_all_items(
    job_store: JobPriorityStore,
    job_factory: Callable[..., Job],
):
    job_store.put(job_factory(id=1))
    job_store.put(job_factory(id=2))
    assert job_store.size() == 2

    job_store.clear_items()

    assert job_store.items == []
    assert job_store.size() == 0


def test_contains_returns_true_for_matching_job_id(
    job_store: JobPriorityStore,
    job_factory: Callable[..., Job],
):
    stored_job = job_factory(id=77, machine_id=5)
    alias_for_same_job_id = job_factory(id=77, machine_id=999)
    job_store.put(stored_job)

    assert alias_for_same_job_id in job_store


def test_contains_returns_false_when_job_not_present(
    job_store: JobPriorityStore,
    job_factory: Callable[..., Job],
):
    job_store.put(job_factory(id=5))

    assert job_factory(id=6) not in job_store


def test_contains_returns_false_for_empty_store(
    job_store: JobPriorityStore,
    job_factory: Callable[..., Job],
):
    assert job_factory(id=1) not in job_store


def test_contains_does_not_mutate_items(
    job_store: JobPriorityStore,
    job_factory: Callable[..., Job],
):
    first = job_factory(id=1, job_type=JobType.SOFTWARE_UPDATE)
    second = job_factory(id=2, job_type=JobType.MECHANICAL_REPAIR)
    job_store.put(first)
    job_store.put(second)

    items_before = list(job_store.items)

    _ = job_factory(id=99) in job_store

    assert job_store.items == items_before


def test_put_raises_attribute_error_when_item_has_no_priority(
    job_store: JobPriorityStore,
):
    with pytest.raises(AttributeError, match="priority"):
        job_store.put(object())  # type: ignore
