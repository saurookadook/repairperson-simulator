class MachineBrokenException(Exception):
    """Exception raised when a machine is broken and cannot operate."""

    def __init__(self, machine_name: str, timestamp: float, *args, **kwargs):
        super().__init__(
            f"Machine '{machine_name}' is broken at {timestamp} seconds.",
            *args,
            **kwargs,
        )
