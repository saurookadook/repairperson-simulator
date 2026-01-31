import random


class Randomizer:
    """A class for generating random numbers based on a specified distribution."""

    def __init__(
        self,
        mean_processing_time: float,
        mean_time_to_failure: float,
        sigma_processing_time: float,
        distribution: str = "normal",  # TODO: maybe don't need this? Or should it be an enum?
        **kwargs
    ):
        self.distribution = distribution
        self.mean_processing_time = mean_processing_time
        self.mean_time_to_failure = mean_time_to_failure
        self.sigma_processing_time = sigma_processing_time
        self.params = kwargs

    def time_per_part(self):
        """Generate a random time for producing a part based on the specified distribution."""
        return abs(
            random.normalvariate(self.mean_processing_time, self.sigma_processing_time)
        )

    def time_to_failure_in_seconds(self):
        """Generate a random time in seconds to failure for a machine based on the specified distribution."""
        return random.expovariate(1 / self.mean_time_to_failure)
