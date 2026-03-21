from __future__ import annotations

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Iterable, Optional

from repairperson_simulator_app.constants import MINUTES_IN_A_WEEK, JobType
from repairperson_simulator_app.simulator.entities import Operator
from repairperson_simulator_app.simulator.machine import Machine

SystemID = int
FaultType = str
RngKey = tuple[SystemID, FaultType]


def spawn_rngs(
    seed: int,
    system_count: int,
    fault_types: Iterable[FaultType],
    *,
    sequence_value: Optional[int] = None,
) -> dict[RngKey, np.random.Generator]:
    rngs: dict[RngKey, np.random.Generator] = dict()
    seed = int(seed)
    sorted_fault_types = sorted(fault_types)
    for system_id in range(system_count):
        entropy_seq = (
            [seed, system_id]
            if sequence_value is None
            else [seed, system_id, sequence_value]
        )
        seed_seq = np.random.SeedSequence(entropy_seq)
        seed_stream = seed_seq.spawn(len(sorted_fault_types))
        for idx, fault_type in enumerate(sorted_fault_types):
            rngs[(system_id, fault_type)] = np.random.default_rng(seed_stream[idx])
    return rngs


def spawn_event_rngs(
    seed: int,
    system_count: int,
    fault_types: Iterable[FaultType],
):
    return spawn_rngs(seed, system_count, fault_types)


class BaseConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")


class JobConfig(BaseConfig):
    """Configuration model for a job."""

    machine_id: int = Field(..., description="The ID of the machine to be repaired.")
    operator_id: int = Field(
        ..., description="The ID of the operator assigned to the job."
    )
    planned_duration: float = Field(
        30.0, description="The planned duration of the repair job (units: minutes)."
    )
    remaining_duration: float = Field(
        30.0, description="The remaining duration of the repair job (units: minutes)."
    )


class MachineConfig(BaseConfig):
    """Configuration for all machines."""

    count: int = Field(5, description="The number of machines in the simulation.")


class OperatorConfig(BaseModel):
    """Configuration model for all operators (repairpeople)."""

    count: int = Field(2, description="The number of operators in the simulation.")
    walk_rate: float = Field(
        1.3, description="The walking rate of the operator (units: meters per second)."
    )


class EngineConfig(BaseConfig):
    """Configuration model for the simulation's engine."""

    fault_rngs: dict[RngKey, np.random.Generator] = Field(default_factory=dict)
    horizon_in_minutes: int = Field(
        default=MINUTES_IN_A_WEEK,
        description="The time horizon for the simulation in minutes.",
    )
    machines: list[Machine] = Field(..., description="A list of machines.")
    operators: list[Operator] = Field(..., description="A list of operators.")
    seed: int = Field(42, description="The random seed for the simulation.")

    @model_validator(mode="after")
    def validated_related_fields(self) -> EngineConfig:
        if not self.fault_rngs:
            system_count = len(self.machines)
            fault_types = [fault_type.name for fault_type in JobType]
            self.fault_rngs = spawn_event_rngs(
                self.seed, system_count, fault_types=fault_types
            )

        return self


class RootConfig(BaseConfig):
    """Root configuration model for the repairperson simulator app."""

    machine_config: MachineConfig = Field(
        ..., description="The configuration for machines in the simulation."
    )
    mean_processing_time: float = Field(
        10.0,
        description="The mean processing time for repairs (units: minutes).",
    )
    mean_time_to_failure: float = Field(
        300.0,
        description="The mean time to failure for machines (units: minutes).",
    )
    operator_config: OperatorConfig = Field(
        ..., description="The configuration for operators in the simulation."
    )
    # TODO: need to add rngs using `numpy`
    seed: int = Field(42, description="The random seed for the simulation.")
    sigma_processing_time: float = Field(
        2.0,
        description="The standard deviation of processing time for repairs (units: minutes).",
    )
