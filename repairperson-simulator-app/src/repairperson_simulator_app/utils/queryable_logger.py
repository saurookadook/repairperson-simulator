import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from repairperson_simulator_app.utils.logging import LogLevelEnum


ROOT_LOGGER = logging.getLogger()


class QueryableLogger:
    def __init__(
        self,
        logger: logging.Logger = ROOT_LOGGER,
        level: int = LogLevelEnum.NOTSET.value,
    ):
        self.logger: logging.Logger = logger
        self.logs: List = []
        self.filters: Set[str] = set()
        self.level: int = level
        self.level_name = LogLevelEnum.get_name_for_value(self.level)

    def log(self, *args, level: int = LogLevelEnum.NOTSET.value):
        # breakpoint()
        level_name = (
            self.level_name
            if level != self.level
            else LogLevelEnum.get_name_for_value(level)
        )

        self.logs.append((level_name, args))
        getattr(self.logger, "log")(level, *args)

    def get_logs(self, level=None):
        if level:
            return [msg for lvl, msg in self.logs if lvl == level]
        return self.logs

    def register_filters(self, *args, filters=None):
        print(args, filters)
        if filters is None:
            return

        for filter_name in args:
            self.filters.add(filter_name)
        for filter_name in filters:
            self.filters.add(filter_name)

    def logify(self, **kwargs):
        print(kwargs)
        should_log = any(key in self.filters for key in kwargs.keys())
        # for key, value in kwargs.items():
        #     if key in self.filters:
        #         self.logger.log(self.level, value)
        if should_log:
            level_from_kwargs = kwargs.get("level", self.level)
            resolved_level = self._resolve_level_value(level_from_kwargs)
            kwargs["level"] = resolved_level
            log_msg = self._build_log_message(kwargs)
            self.log(log_msg, level=resolved_level)

    def _build_log_message(self, kwargs: Dict[str, Any]) -> str:
        message = ""
        now = datetime.now().isoformat()
        for key, value in kwargs.items():
            message += f"{now} ( {self.level_name.upper()} ) [{key}] {value}\n"
        return message

    def _resolve_level_value(self, level: Any) -> int:
        if isinstance(level, LogLevelEnum):
            return level.value
        elif isinstance(level, int) and level in LogLevelEnum.level_values():
            return level
        elif isinstance(level, str):
            return LogLevelEnum.get_value_for_name(level)

        breakpoint()
        return LogLevelEnum.NOTSET.value
