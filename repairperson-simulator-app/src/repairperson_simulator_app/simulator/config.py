from __future__ import annotations

from pydantic import BaseModel, Field
from typing import List

from repairperson_simulator_app.constants import MINUTES_IN_A_WEEK


class BaseConfig(BaseModel):
    class Config:
        extra = "forbid"


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
    """Configuration model for a machine."""

    name: str = Field(..., description="The name of the machine.")
    failure_rate: float = Field(
        ..., description="The failure rate of the machine (failures per minute)."
    )


class OperatorConfig(BaseModel):
    """Configuration model for an operator (repairperson)."""

    name: str = Field(..., description="The name of the operator.")
    repair_time: float = Field(
        30.0,
        description="The time it takes for the operator to repair a machine (units: minutes).",
    )
    walk_rate: float = Field(
        1.3, description="The walking rate of the operator (units: meters per second)."
    )


class EngineConfig(BaseConfig):
    """Configuration model for the simulation's engine."""

    horizon: int = Field(
        MINUTES_IN_A_WEEK, description="The time horizon for the simulation in minutes."
    )
    machines: List[MachineConfig] = Field(
        ..., description="A list of machine configurations."
    )
    operators: List[OperatorConfig] = Field(
        ..., description="A list of operator configurations."
    )


class RootConfig(BaseConfig):
    """Root configuration model for the repairperson simulator app."""

    mean_processing_time: float = Field(
        10.0,
        description="The mean processing time for repairs (units: minutes).",
    )
    mean_time_to_failure: float = Field(
        300.0,
        description="The mean time to failure for machines (units: minutes).",
    )
    number_of_machines: int = Field(
        5, description="The number of machines in the simulation."
    )
    number_of_operators: int = Field(
        2, description="The number of operators in the simulation."
    )
    seed: int = Field(42, description="The random seed for the simulation.")
    sigma_processing_time: float = Field(
        2.0,
        description="The standard deviation of processing time for repairs (units: minutes).",
    )
