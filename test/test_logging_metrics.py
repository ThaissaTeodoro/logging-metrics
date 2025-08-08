import os
import sys
import logging
import json
import pytest
import time

from logging_metrics.core import (
    ColoredFormatter,
    JSONFormatter,
    create_file_handler,
    create_timed_file_handler,
    create_console_handler,
    get_logger,
    setup_file_logging,
    LogTimer,
    log_spark_dataframe_info,
    LogMetrics,
    _make_timezone_converter,
)

try:
    from pyspark.sql import SparkSession

    spark_available = True
except ImportError:
    spark_available = False


def test_colored_formatter_colors(monkeypatch):
    """Verify that ANSI color codes are applied in the logs."""
    record = logging.LogRecord("my_logger", logging.WARNING, "path", 1, "test", None, None)
    formatter = ColoredFormatter(use_colors=True)
    output = formatter.format(record)
    assert "\033[" in output  # Has color code
    assert "WARNING" in output


def test_colored_formatter_no_colors():
    """Check that no colors are applied if use_colors=False."""
    record = logging.LogRecord("my_logger", logging.ERROR, "path", 1, "error", None, None)
    formatter = ColoredFormatter(use_colors=False)
    output = formatter.format(record)
    assert "\033[" not in output


def test_json_formatter_simple():
    """Test that JSON formatted log contains all basic fields."""
    record = logging.LogRecord(
        name="json_logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=123,
        msg="Test message",
        args=None,
        exc_info=None,
        func="test_func",
    )
    formatter = JSONFormatter()
    out = formatter.format(record)
    as_json = json.loads(out)
    assert as_json["level"] == "INFO"
    assert as_json["name"] == "json_logger"
    assert "message" in as_json


def test_json_formatter_exception():
    """Test that exception info is serialized."""
    try:
        raise ValueError("Error!")
    except ValueError:
        record = logging.LogRecord(
            "logger",
            logging.ERROR,
            __file__,
            88,
            "msg with error",
            None,
            sys.exc_info(),
            func="fail",
        )
        formatter = JSONFormatter()
        j = json.loads(formatter.format(record))
        assert "exception" in j
        assert "ValueError" in j["exception"]["type"]


def test_create_file_handler_and_rotation(tmp_log_dir):
    """Create a log file with size-based rotation."""
    log_path = os.path.join(tmp_log_dir, "test.log")
    handler = create_file_handler(log_file=log_path, max_bytes=100, backup_count=2)
    logger = logging.getLogger("test_file")
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    # Write logs until rotation happens
    for i in range(30):
        logger.info("line %d - abcdefghijklmnopqrstuvwxyz", i)
    handler.flush()
    # Original and backup files should exist
    files = [f for f in os.listdir(tmp_log_dir) if f.startswith("test")]
    assert any(".log" in f for f in files)


def test_create_timed_file_handler(tmp_log_dir):
    """Create a time-based rotation handler without error."""
    log_path = os.path.join(tmp_log_dir, "t.log")
    handler = create_timed_file_handler(log_file=log_path, interval=1, backup_count=1)
    logger = logging.getLogger("test_time")
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    logger.info("first")
    handler.flush()
    files = os.listdir(tmp_log_dir)
    assert "t.log" in files


def test_create_console_handler_stdout(monkeypatch):
    """Verify console handler to stdout."""
    handler = create_console_handler(level=logging.INFO, use_colors=False)
    assert isinstance(handler, logging.StreamHandler)
    assert handler.level == logging.INFO


def test_configure_basic_logging_and_get_logger(caplog):
    logger = get_logger("my.logger", level=logging.DEBUG, propagate=True, caplog_friendly=True)
    with caplog.at_level(logging.DEBUG):
        logger.info("info message")
        logger.error("error message")
    msgs = " ".join(r.getMessage() for r in caplog.records)
    assert "info message" in msgs
    assert "error message" in msgs


def test_setup_file_logging(tmp_log_dir):
    """Test logger with configured file and console handlers."""
    logger = setup_file_logging(
        logger_name="testlog",
        log_folder=".",
        log_dir=tmp_log_dir + os.sep,
        file_prefix="prefix",
        add_console=False,
        json_format=True,
        rotation="size",
        backup_count=1,
    )
    logger.info("Log JSON test")
    # Ensure that a log file is generated
    files = os.listdir(tmp_log_dir)
    assert any(a.endswith(".json") for a in files)
    logger.close()  # Test closing


def test_make_timezone_converter():
    """Test timezone converter."""
    converter = _make_timezone_converter("America/Sao_Paulo")
    t_struct = converter(1710000000)
    assert hasattr(t_struct, "tm_year")
    assert t_struct.tm_year > 2000


def test_get_logger_custom_handlers(monkeypatch):
    """Test get_logger with custom handlers."""
    from unittest.mock import MagicMock

    handler = MagicMock(spec=logging.Handler)
    logger = get_logger("custom", level=logging.WARNING, handlers=[handler])
    assert handler in logger.handlers
    assert logger.level == logging.WARNING


def test_logtimer_context_and_decorator(capsys):
    """Test LogTimer as context manager and decorator."""
    import sys

    logger = get_logger("timer")
    # Remove all old handlers
    for h in logger.handlers[:]:
        logger.removeHandler(h)
    # Add handler for stdout
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    with LogTimer(logger, "Context Operation"):
        time.sleep(0.1)

    @LogTimer.as_decorator(logger, "Decorator Operation")
    def task():
        time.sleep(0.1)
        return 42

    result = task()
    assert result == 42
    out = capsys.readouterr().out
    assert "Completed: Context Operation" in out or "Completed: Decorator Operation" in out


def test_logmetrics_increment_set_log_logall(capsys):
    """Test LogMetrics: increment, set, timers, and log_all."""
    import sys

    logger = get_logger("metrics")
    # Remove all old handlers
    for h in logger.handlers[:]:
        logger.removeHandler(h)
    # Add handler for stdout
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    metrics = LogMetrics(logger)
    metrics.increment("items", 2)
    metrics.set("batch", 10)
    metrics.start("op1")
    time.sleep(0.05)
    metrics.stop("op1")
    metrics.log("items")
    metrics.log("batch")
    metrics.log("op1")
    metrics.log_all()
    out = capsys.readouterr().out
    assert "Counter 'items': 2" in out


@pytest.mark.skipif(not spark_available, reason="PySpark not available")
def test_log_spark_dataframe_info_basic(tmp_path):
    """Test log_spark_dataframe_info for PySpark DataFrames."""
    spark = SparkSession.builder.master("local[1]").appName("logdf").getOrCreate()
    logger = get_logger("sparkdf", level=logging.INFO)
    from pyspark.sql import Row

    df = spark.createDataFrame([Row(a=1, b=2), Row(a=2, b=3)])
    log_spark_dataframe_info(
        df, logger, name="TestDF", show_schema=True, show_sample=True, sample_rows=2
    )
    # Test that count, schema, sample, and stats do not raise exceptions
    spark.stop()


def test_log_spark_dataframe_info_none(caplog):
    """Log warning if DataFrame is None."""
    logger = get_logger("test", level=logging.INFO, propagate=True, caplog_friendly=True)
    log_spark_dataframe_info(None, logger, name="DFNone")
    assert any("DataFrame is None" in r.getMessage() for r in caplog.records)
