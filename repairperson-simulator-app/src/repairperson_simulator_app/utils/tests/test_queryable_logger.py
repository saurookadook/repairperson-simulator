import pytest

from repairperson_simulator_app.utils.logging import LogLevelEnum
from repairperson_simulator_app.utils.queryable_logger import QueryableLogger


def test_queryable_logger_get_logs():
    logger = QueryableLogger()
    logger.log("info", "This is an info message.")
    logger.log("error", "This is an error message.")
    logger.log("debug", "This is a debug message.")

    assert len(logger.get_logs()) == 3

    expected_logs = [
        ("NOTSET", ("info", "This is an info message.")),
        ("NOTSET", ("error", "This is an error message.")),
        ("NOTSET", ("debug", "This is a debug message.")),
    ]

    result_logs = logger.get_logs()

    for result, expected in zip(result_logs, expected_logs):
        res_level_str, res_args_tuple = result
        level_str, kwarg_values = expected

        assert level_str == res_level_str
        assert kwarg_values == res_args_tuple


@pytest.mark.skip(reason="Implement this thing later :]")
def test_queryable_logger_get_logs_with_level_arg():
    logger = QueryableLogger()
    logger.register_filters(filters=["level", "message"])
    logger.logify(level="info", message="This is an info message.")
    logger.logify(level="error", message="This is an error message.")
    logger.logify(level="debug", message="This is a debug message.")

    expected_logs = [
        ("INFO", ("info", "This is an info message.")),
        ("ERROR", ("error", "This is an error message.")),
        ("DEBUG", ("debug", "This is a debug message.")),
    ]

    breakpoint()
    assert len(logger.get_logs()) == 3
    assert logger.get_logs("info") == ["This is an info message."]
    assert logger.get_logs("error") == ["This is an error message."]
    assert logger.get_logs("debug") == ["This is a debug message."]


def test_queryable_logger_register_filters():
    logger = QueryableLogger()
    logger.register_filters(filters=["level", "message"])
    assert "level" in logger.filters
    assert "message" in logger.filters

    logger.register_filters(filters=["item", "name"])
    logger.logify(item=LogLevelEnum, question="What is life?")
    logger.logify(count=4)
    logger.logify(level=LogLevelEnum.CRITICAL, message="This is a critical message.")
    logger.logify(name="method_name", value=42)

    expected_logs = [
        ("NOTSET", (LogLevelEnum, "What is life?")),
        ("NOTSET", (LogLevelEnum.CRITICAL.value, "This is a critical message.")),
        ("NOTSET", ("method_name", 42)),
    ]

    result_logs = logger.get_logs()

    for result, expected in zip(result_logs, expected_logs):
        res_level_str, res_args_tuple = result
        level_str, kwarg_values = expected

        assert level_str == res_level_str

        res_msg = res_args_tuple[0]
        for value in kwarg_values:
            assert str(value) in res_msg
