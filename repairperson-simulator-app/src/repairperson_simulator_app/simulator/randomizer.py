import random


class Randomizer:
    """A class for generating random numbers based on a specified distribution."""

    def __init__(
        self,
        distribution: str,
        mean_processing_time: float,
        mean_time_to_failure: float,
        sigma_processing_time: float,
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

    def time_to_failure(self):
        """Generate a random time to failure for a machine based on the specified distribution."""
        return random.expovariate(1 / self.mean_time_to_failure)
