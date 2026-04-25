from __future__ import annotations

import logging
import simpy
from typing import TYPE_CHECKING, cast

from repairperson_simulator_app.constants import EVENT_POLLING_INTERVAL, EventType
from repairperson_simulator_app.events import (
    Event,
    OnJobAssignedEvent,
    OnJobAssignedEventDetails,
    OnJobQueuedEvent,
)
from repairperson_simulator_app.simulator.entities import Job, Operator
from repairperson_simulator_app.simulator.event_logger import EventLogger
from repairperson_simulator_app.utils.event_observer import event_observer


if TYPE_CHECKING:
    from repairperson_simulator_app.simulator.config import EngineConfig, RootConfig
    from repairperson_simulator_app.simulator.job_manager import JobManager
    from repairperson_simulator_app.simulator.machine import Machine
    from repairperson_simulator_app.simulator.machine_mediator import MachineMediator
    from repairperson_simulator_app.simulator.operator_filter_store import (
        OperatorFilterStore,
    )

# TODO: delete me later :D
from rich import inspect as ri
from rich.pretty import pretty_repr as pr


class OperatorManager:

    def __init__(
        self,
        env: simpy.Environment,
        engine_config: EngineConfig,
        root_config: RootConfig,
        job_manager: JobManager,
        machine_mediator: MachineMediator,
        operator_filter_store: OperatorFilterStore,
    ):
        self.env = env
        self.engine_config = engine_config
        self.root_config = root_config
        self.job_manager = job_manager
        self.machine_mediator = machine_mediator
        self.operator_filter_store = operator_filter_store

        self.logger: logging.Logger = logging.getLogger(self.__class__.__name__)

        self.event_logger = EventLogger(self.env)
        # TODO: maybe this should be an `indexed_operators` dict?
        self.operators = self.engine_config.operators
        self.operator_processes: list[simpy.Process | None] = [None] * len(
            self.operators
        )
        self.preemption_check_interval = EVENT_POLLING_INTERVAL

    def setup_listeners(self):
        event_observer.add_event_listener(
            EventType.ON_JOB_QUEUED.value, self.handle_job_queued
        )
        event_observer.add_event_listener(
            EventType.ON_ASSIGN_OPERATOR_TO_JOB.value,
            self.handle_assign_operator_to_job,
        )

    def handle_job_queued(self, event: Event):
        event = cast(OnJobQueuedEvent, event)
        self.logger.debug(
            f"    {self.handle_job_queued.__qualname__} received event    ".center(
                180, "|"
            )
        )
        # self.logger.debug(f"\n{pr(dict(event_type=event.type, details=event.details))}")
        if event.details is None or event.details.job is None:
            raise ValueError(
                f"[{self.handle_job_queued.__qualname__}] 'event' is missing details about job."
            )
        self.logger.debug(
            f"    Maybe dispatching operator for job '{event.details.job.id}' in process    ".center(
                180, "="
            )
        )
        self.env.process(self.maybe_dispatch_operator(event.details.job))

    def handle_assign_operator_to_job(self, event: Event):
        event = cast(OnJobAssignedEvent, event)
        evt_details = event.details
        self.logger.debug(
            f"    '{self.handle_assign_operator_to_job.__qualname__}'    ".center(
                180, "+"
            )
        )
        self.logger.debug(f"\n{pr(event)}")
        self.logger.debug("+" * 180)

        if evt_details is None:
            raise ValueError(
                f"[{self.handle_assign_operator_to_job.__qualname__}] 'event' is missing details about broken machine."
            )

        operator = self.operators[evt_details.operator_id]
        job = evt_details.job
        priority = job.priority

        self.operator_processes[operator.id] = self.env.process(
            self.create_operator_process(operator, priority, job)
        )

    def maybe_dispatch_operator(self, job: Job):
        self.logger.debug(
            f"    Maybe dispatching operator for job '{job.id}'    ".center(180, "?")
        )
        _, job = yield self.job_manager.get_next_job()
        # self.logger.debug(f"\n{pr(dict(maybe_job=job))}")
        operator_get = self.operator_filter_store.get_first_available_for_job(job)
        self.logger.debug(
            f"    Found operator for job? '{type(operator_get)}'    ".center(180, "-")
        )
        # self.logger.debug(f"\n{pr(operator_get)}")
        if operator_get is None:
            self.job_manager.re_put_job_to_store(job)
            return simpy.Event(self.env).succeed(
                f"No Operator found for job '{job.id}' at machine '{job.machine_id}'"
            )
            # .fail(
            #     Exception(
            #         f"No Operator found for job '{job.id}' at machine '{job.machine_id}'"
            #     )
            # )

        operator = yield operator_get
        self.logger.debug(
            f"    Dispatching operator '{operator.id}' for job '{job.id}'    ".center(
                180, "!"
            )
        )
        self.logger.debug(f"\n{pr(operator)}")
        self.logger.debug("!" * 180)
        event_observer.dispatch_event(
            details=OnJobAssignedEventDetails(job, operator_id=operator.id),
            event_type=EventType.ON_ASSIGN_OPERATOR_TO_JOB.value,
        )

    def create_operator_process(self, operator: Operator, priority: int, job: Job):
        machine = self.machine_mediator.get_machine_by_id(job.machine_id)
        self.logger.debug(
            f"    Created process for operator '{operator.id}' for job '{job.id}' at machine '{machine.id}'    ".center(
                180, "*"
            )
        )

        operator = self.operator_filter_store.update_operator(
            operator.id, current_job=job, machine_location=machine.id
        )
        # ri(operator)
        # breakpoint()
        job.add_operator_and_recalc_service_time(operator.id)
        # TODO: implement this later
        # if len(job.assigned_operator_ids) < machine.capacity:
        #     self.job_manager.re_put_job_to_store(job)

        walk_time_minutes = self._calc_walk_time(operator, job.machine_id)
        self.logger.debug(
            f"--------  Calculated walk time for operator '{operator.id}' to machine '{machine.id}': {walk_time_minutes:.2f} minutes"
        )
        if walk_time_minutes > 0:
            yield self.env.timeout(walk_time_minutes)

        operator = self.operator_filter_store.update_operator_for_arrival_at_machine(
            operator.id, job.machine_id
        )

        self.logger.debug(
            f"--------  Starting service for job '{job.id}' with operator '{operator.id}' at machine '{machine.id}'"
        )
        self._start_service(job, operator, machine)

        completed = yield from self._service_with_preemption(job, operator)
        self.logger.debug(
            f"   Service completed for job '{job.id}'? {completed}    ".center(180, "@")
        )
        self.logger.debug(
            pr(
                dict(
                    completed=completed,
                    job_id=job.id,
                    machine_id=job.machine_id,
                    operator_id=operator.id,
                )
            )
        )

        if completed:
            self._complete_service(job, operator, machine)

            # TODO: implement this later
            # if self.job_manager.job_store.size() == 0:
            #     yield from self._return_to_resting_location(job, operator, machine)
        else:
            # self.logger.debug(f"\n{pr(job)}")
            yield self.job_manager.put_job_to_store(job)

        _, maybe_open_job = self.job_manager.peek_highest_priority_job()

        if maybe_open_job is not None:
            self.logger.debug(
                f"    Operator '{operator.id}' checking for next job to work on after completing job '{job.id}'    ".center(
                    180, "%"
                )
            )
            self.logger.debug(f"\n{pr(maybe_open_job)}")
            self.logger.debug("%" * 180)
            # yield from self.maybe_dispatch_operator(maybe_open_job)
            _, next_job = yield self.job_manager.get_next_job()
            event_observer.dispatch_event(
                details=OnJobAssignedEventDetails(next_job, operator_id=operator.id),
                event_type=EventType.ON_ASSIGN_OPERATOR_TO_JOB.value,
            )
            return

        yield self.operator_filter_store.put(operator)

    def _start_service(self, job: Job, operator: Operator, machine: Machine):
        job.add_operator_and_recalc_service_time(operator.id)
        operator = self.operator_filter_store.update_operator_for_job_start(
            operator.id, job
        )
        self.event_logger.log_event(
            event_type=EventType.JOB_STARTED.value,
            details=dict(
                job_id=job.id,
                job_type=job.job_type,
                machine_id=job.machine_id,
                operator_id=operator.id,
                operator_name=operator.name,
            ),
        )

    def _service_with_preemption(self, job: Job, operator: Operator):
        machine = self.machine_mediator.get_machine_by_id(job.machine_id)

        while job.remaining_duration > 0:
            work_time_until_horizon = min(
                self.preemption_check_interval,
                self._calc_remaining_work_time(job),
            )
            if work_time_until_horizon <= 0:
                return False

            yield self.env.timeout(work_time_until_horizon)

            job.remaining_duration = self._get_adjusted_remaining_work_time(
                job, operator, work_time_until_horizon
            )

            if job.remaining_duration <= 0:
                return True

            if self._should_work_be_preempted(operator):
                self._handle_preempted_work(job, operator, machine)
                return False

        return True

    def _complete_service(self, job: Job, operator: Operator, machine: Machine):
        if not job.is_completed:
            self.job_manager.update_completed_job(job, machine)
        operator = self.operator_filter_store.update_operator_for_job_complete(
            operator.id
        )
        job.is_completed = True

    def _handle_preempted_work(self, job: Job, operator: Operator, machine: Machine):
        # self.job_manager.handle_preempt_start(job, operator, machine)
        self.operator_filter_store.update_operator_for_preemption(operator.id)

    def _calc_walk_time(self, operator: Operator, machine_id: int) -> float:
        travel_steps = abs(machine_id - operator.get_machine_location())
        self.logger.debug(
            f"    '{self._calc_walk_time.__qualname__}' :: {travel_steps=}, operator_walk_rate={operator.walk_rate}"
        )
        return travel_steps * operator.walk_rate

    def _calc_remaining_work_time(self, job: Job) -> float:
        return self._calc_remaining_time(job.remaining_duration)

    def _calc_remaining_time(self, time_in_minutes: float) -> float:
        remaining_to_horizon = max(
            0.0, self.engine_config.horizon_in_minutes - self.env.now
        )
        return min(time_in_minutes, remaining_to_horizon)

    def _get_adjusted_remaining_work_time(
        self, job: Job, operator: Operator, work_time_until_horizon: float
    ) -> float:
        """
        TODO: This method is a bit of a hack to deal with concurrent calls from different operators

        Args:
            job (``Job``): The job for which the remaining work time is being calculated.
            operator (``Operator``): The operator performing the job.
            work_time_until_horizon (``float``): The work time until the simulation horizon is reached.

        Returns:
            ``float``: The adjusted remaining work time for the job.
        """
        adj_work_time = job.remaining_duration - work_time_until_horizon

        if (
            len(job.assigned_operator_ids) > 0
            and sorted(job.assigned_operator_ids)[0] != operator.id
        ):
            adj_work_time = job.remaining_duration

        return max(adj_work_time, 0)

    def _should_work_be_preempted(self, operator: Operator) -> bool:
        if operator.current_job is None:
            self.logger.warning(
                f"Operator {operator.id} has no current job but is being checked for preemption. This should not happen."
            )
            return True

        priority_key = operator.current_job.priority
        maybe_higher_prio, maybe_higher_job = (
            self.job_manager.peek_higher_priority_job_with_open_capacity(priority_key)
        )

        if maybe_higher_prio is None or maybe_higher_job is None:
            return False

        other_available_operators = (
            self.operator_filter_store.get_other_available_operators_for_job(
                maybe_higher_job, operator
            )
        )

        if len(other_available_operators) > 0:
            return False

        return operator.is_available_for_job(maybe_higher_job)

    def _is_closest_interruptible_operator_to_machine(
        self, target_operator: Operator, job: Job
    ) -> bool:
        """
        Returns ``True`` if ``target_operator`` can reach ``job.machine_id`` and there is no other
        interruptible ``Operator`` that can also reach ``job.machine_id`` and is either closer to it
        or at the same distance with a smaller ``id`` than ``target_operator``.
        """

        target_distance = target_operator.get_distance_to_machine(job.machine_id)

        for operator in self.operator_filter_store.operators:
            if operator.id == target_operator.id:
                continue

            if not operator.is_interruptible():
                continue

            operator_distance = operator.get_distance_to_machine(job.machine_id)

            if operator_distance < target_distance or (
                operator_distance == target_distance
                and operator.id < target_operator.id
            ):
                return False

        return True
