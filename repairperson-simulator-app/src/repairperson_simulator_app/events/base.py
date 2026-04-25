from __future__ import annotations

# from abc import ABC, abstractmethod
from dataclasses import dataclass
from rich.pretty import pretty_repr as pr
from typing import Generic, Optional, TypeVar


Details = TypeVar("Details")


@dataclass
class Event(Generic[Details]):
    type: str
    timestamp: float
    details: Optional[Details]

    def get_csv_row(self) -> dict:
        row_dict = dict(
            event_type=self.type,
            timestamp=self.timestamp,
        )

        evt_details = self.details

        if isinstance(evt_details, dict):
            for key, value in evt_details.items():
                if key == "job":
                    row_dict["job_id"] = value.id
                    row_dict["job_planned_duration"] = value.planned_duration
                    row_dict["job_remaining_duration"] = value.remaining_duration
                    row_dict["job_type"] = value.job_type.value
                    row_dict["machine_id"] = value.machine_id
                elif key == "machine":
                    row_dict["machine_id"] = value.id
                    row_dict["machine_name"] = value.name
                    row_dict["machine_parts_made"] = value.parts_made
                else:
                    row_dict[key] = value

        return row_dict


class GenericEventDetails(dict):
    def __repr__(self):
        return pr(self.__dict__)
