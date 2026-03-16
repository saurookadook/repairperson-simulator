from abc import ABC, abstractmethod
from simpy.resources.store import StoreGet, StorePut
from typing import Any


class AbstractBaseStore(ABC):
    @abstractmethod
    def get(self) -> StoreGet:
        """Get an item from the store."""
        pass

    @abstractmethod
    def put(self, item: Any) -> StorePut:
        """Put an item into the store."""
        pass

    @abstractmethod
    def size(self) -> int:
        """Return the number of items currently in the store."""
        pass

    @property
    @abstractmethod
    def items(self) -> list:
        """Return a list of items currently in the store."""
        pass
