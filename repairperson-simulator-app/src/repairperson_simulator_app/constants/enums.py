from enum import Enum, auto


class JobType(Enum):
    ELECTRICAL_REPAIR = auto()
    MECHANICAL_REPAIR = auto()
    ELECTRICAL_MAINTENANCE = auto()
    MECHANICAL_MAINTENANCE = auto()
    SOFTWARE_UPDATE = auto()


class MachineStatus(Enum):
    BROKEN = auto()
    OPERATOR_EN_ROUTE = auto()
    NEEDS_MAINTENANCE = auto()
    WORKING = auto()
