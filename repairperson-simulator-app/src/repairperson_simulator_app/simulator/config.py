from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
from typing import List

from repairperson_simulator_app.constants import MINUTES_IN_A_WEEK
from repairperson_simulator_app.simulator.entities import Operator
from repairperson_simulator_app.simulator.machine import Machine


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

    horizon: int = Field(
        default=MINUTES_IN_A_WEEK,
        description="The time horizon for the simulation in minutes.",
    )
    machines: List[Machine] = Field(..., description="A list of machines.")
    operators: List[Operator] = Field(..., description="A list of operators.")


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
