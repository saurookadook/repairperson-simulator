from __future__ import annotations

import numpy as np
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationInfo,
    field_validator,
    model_validator,
)
from typing import Iterable, Optional

from repairperson_simulator_app.constants import MINUTES_IN_A_WEEK, JobType
from repairperson_simulator_app.constants.types import FaultType, RngKey
from repairperson_simulator_app.simulator.entities import Operator
from repairperson_simulator_app.simulator.machine import Machine
from repairperson_simulator_app.utils.stats_params import (
    mu_and_sigma_from_median_and_cv,
    mu_and_sigma_from_p50_and_p90,
)


def is_non_negative_number(value: float | int, info: ValidationInfo) -> float | int:
    if value < 0:
        raise ValueError(f"{info.field_name} must be a non-negative number.")
    return value


def is_positive_number(value: float | int, info: ValidationInfo) -> float | int:
    if value <= 0:
        raise ValueError(f"{info.field_name} must be a positive number.")
    return value


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


class FaultDistributionConfig(BaseConfig):
    # TODO: I think a bunch of these things should probably go into the `JobConfig`

    dist: str = Field(default="lognormal")
    set_time_as: str = Field(
        default="median", pattern=r"^(mean|median|mode|percentiles)$"
    )
    set_time: Optional[float] = None
    cv: Optional[float] = None
    p50: Optional[float] = None
    p90: Optional[float] = None

    @field_validator("cv")
    @classmethod
    def _positive_cv(
        cls, value: Optional[float], info: ValidationInfo
    ) -> Optional[float]:
        if value is None:
            return value
        return is_positive_number(value, info)

    @field_validator("set_time")
    @classmethod
    def _positive_time(
        cls, value: Optional[float], info: ValidationInfo
    ) -> Optional[float]:
        if value is None:
            return value
        return is_positive_number(value, info)

    def to_mu_sigma(self) -> tuple[float, float]:
        if self.set_time_as == "percentiles":
            if self.p50 is None or self.p90 is None:
                raise ValueError(
                    "'p50' and 'p90' must be provided when 'set_time_as' is 'percentiles'."
                )
            return mu_and_sigma_from_p50_and_p90(self.p50, self.p90)
        if self.set_time is None or self.cv is None:
            raise ValueError(
                "'set_time' and 'cv' must be provided when 'set_time_as' is not 'percentiles'."
            )
        return mu_and_sigma_from_median_and_cv(self.set_time, self.cv)


class FaultConfig(BaseConfig):
    """Configuration model for a machine fault."""

    dist_type: str = "poisson"
    distribution_cfg: FaultDistributionConfig = Field(
        default_factory=FaultDistributionConfig
    )
    job_type: JobType = Field(..., description="The type of repair job needed.")
    rate_per_system_per_hour: float = Field(default=1.0)
    rate_per_system_per_minute: float
    repair_time_in_min: float = Field(
        30.0, description="The time it takes to repair the machine (units: minutes)."
    )

    @model_validator(mode="after")
    def compute_rate_per_minute(self) -> FaultConfig:
        self.rate_per_system_per_minute = self.rate_per_system_per_hour / 60.0
        return self


class MachineConfig(BaseConfig):
    """Configuration for all machines."""

    count: int = Field(5, description="The number of machines in the simulation.")


class OperatorConfig(BaseModel):
    """Configuration model for all operators (repairpeople)."""

    count: int = Field(2, description="The number of operators in the simulation.")
    walk_rate: float = Field(
        1.3, description="The walking rate of the operator (units: meters per second)."
    )


class RootConfig(BaseConfig):
    """Root configuration model for the repairperson simulator app."""

    fault_rngs_map: dict[RngKey, np.random.Generator] = Field(default_factory=dict)
    fault_types_map: dict[FaultType, FaultConfig] = Field(default_factory=dict)
    machine_config: MachineConfig = Field(
        ..., description="The configuration for machines in the simulation."
    )
    # mean_processing_time: float = Field(
    #     10.0,
    #     description="The mean processing time for repairs (units: minutes).",
    # )
    # mean_time_to_failure: float = Field(
    #     300.0,
    #     description="The mean time to failure for machines (units: minutes).",
    # )
    operator_config: OperatorConfig = Field(
        ..., description="The configuration for operators in the simulation."
    )
    seed: int = Field(42, description="The random seed for the simulation.")
    # sigma_processing_time: float = Field(
    #     2.0,
    #     description="The standard deviation of processing time for repairs (units: minutes).",
    # )

    # TODO: move rng generation here?
    @model_validator(mode="after")
    def validated_related_fields(self) -> RootConfig:
        if not self.fault_rngs_map:
            system_count = self.machine_config.count
            fault_types = [fault_type.name for fault_type in JobType]
            self.fault_rngs_map = spawn_event_rngs(
                self.seed, system_count, fault_types=fault_types
            )

        return self


class EngineConfig(BaseConfig):
    """Configuration model for the simulation's engine."""

    horizon_in_minutes: int = Field(
        default=MINUTES_IN_A_WEEK,
        description="The time horizon for the simulation in minutes.",
    )
    machines: list[Machine] = Field(..., description="A list of machines.")
    operators: list[Operator] = Field(..., description="A list of operators.")
