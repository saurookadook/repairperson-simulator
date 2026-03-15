import threading


class SingletonMeta(type):
    """A metaclass that creates a Singleton instance of the decorated class.

    Partially inpsired by implementation here:
    - https://gist.github.com/werediver/4396488
    """

    _instances = {}
    __singleton_lock = threading.Lock()
    __singleton_instance = None

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls.__singleton_lock:
                if not cls.__singleton_instance:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        return cls._instances[cls]
