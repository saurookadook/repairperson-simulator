from __future__ import annotations

import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from repairperson_simulator_app.constants.types import FaultType, SystemID
    from repairperson_simulator_app.simulator.config import RootConfig


# TODO:
# - maybe move randomization utils here?
class Randomizer:
    """A class for generating random numbers based on a specified distribution."""

    def __init__(
        self,
        root_config: RootConfig,
        **kwargs,
    ):
        self.root_config = root_config
        self.fault_types_map = self.root_config.fault_types_map
        self.rngs_map = self.root_config.fault_rngs_map
        self.params = kwargs

    def time_per_part(self):
        """Generate a random time for producing a part based on the specified distribution."""
        raise NotImplementedError(
            "This method should be implemented based on the desired distribution."
        )
        # return abs(
        #     random.normalvariate(self.mean_processing_time, self.sigma_processing_time)
        # )

    def time_to_failure_in_seconds(self):
        """Generate a random time in seconds to failure for a machine based on the specified distribution."""
        raise NotImplementedError(
            "This method should be implemented based on the desired distribution."
        )

    def time_to_failure_in_minutes_for_system_and_fault_type(
        self, system_id: SystemID, fault_type: FaultType
    ) -> float:
        """Generate a random time in minutes to failure for a machine based on the specified distribution."""
        fault_cfg = self.fault_types_map.get(fault_type, None)
        if fault_cfg is None:
            raise ValueError(
                f"No fault distribution config found for fault type: {fault_type}"
            )

        rate_per_min = fault_cfg.rate_per_system_per_minute
        rng = self.rngs_map[(system_id, fault_type)]
        return rng.exponential(1.0 / rate_per_min)
