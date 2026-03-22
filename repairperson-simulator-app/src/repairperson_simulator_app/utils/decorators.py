from __future__ import annotations

from functools import wraps
from typing import Any, Callable, Generator


from repairperson_simulator_app.simulator.exceptions import HorizonReached


def is_horizon_reached_exception(exception: Exception) -> bool:
    return isinstance(exception, HorizonReached)


def should_raise_horizon_reached_exception(exception: Exception) -> bool:
    return is_horizon_reached_exception(exception) and getattr(
        exception, "should_bubble", False
    )


def exceptions_guard(*exceptions):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs) -> Generator[Any, Any, Any | None]:
            call_result = func(*args, **kwargs)
            if hasattr(call_result, "__next__"):
                try:
                    # delegate to inner generator
                    yield from call_result
                except exceptions:
                    return

            try:
                return call_result
            except exceptions:
                return

        return wrapper

    return decorator


def event_details_guard(event_details_type):
    """TODO: improve typing"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            _self = args[0]
            event = kwargs["details"] if "event" in kwargs else args[1]
            details = event.details
            if not isinstance(details, event_details_type):
                try:
                    details = event_details_type(**details)
                except Exception as e:
                    raise ValueError(
                        f"[{func.__qualname__}]"
                        f"`event.details` is incompatible with `{event_details_type.name}`."
                        f"\n----Received details: '{details}' ()"
                    ) from e
            event.details = details
            return func(*args, **kwargs)

        return wrapper

    return decorator


def horizon_guard(func):
    @wraps(func)
    def wrapper(*args, **kwargs) -> Generator[Any, Any, Any | None]:
        call_result = func(*args, **kwargs)
        if hasattr(call_result, "__next__"):
            try:
                # delegate to inner generator
                yield from call_result
            except Exception as e:
                if not is_horizon_reached_exception(
                    e
                ) or should_raise_horizon_reached_exception(e):
                    raise

        try:
            return call_result
        except Exception as e:
            if not is_horizon_reached_exception(
                e
            ) or should_raise_horizon_reached_exception(e):
                raise

    return wrapper
