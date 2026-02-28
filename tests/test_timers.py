import json
import logging
import os
import time
from unittest.mock import patch

import pytest

from logging_metrics.core import (
    ColoredFormatter,
    JSONFormatter,
    LogMetrics,
    LogTimer,
    configure_basic_logging,
    create_console_handler,
    create_file_handler,
    create_timed_file_handler,
    get_logger,
    log_spark_dataframe_info,
    setup_file_logging,
)

try:
    from pyspark.sql import SparkSession

    spark_available = True
except ImportError:
    spark_available = False


# ======== TESTES PARA LogTimer ========


def test_logtimer_validation_errors():
    """Test LogTimer initialization validation errors."""
    # Test invalid logger type
    with pytest.raises(TypeError, match="logger must be a logging.Logger instance"):
        LogTimer("not_a_logger", "test")

    # Test empty operation name
    logger = logging.getLogger("test")
    with pytest.raises(ValueError, match="operation_name must be a non-empty string"):
        LogTimer(logger, "")

    with pytest.raises(ValueError, match="operation_name must be a non-empty string"):
        LogTimer(logger, "   ")  # Only whitespace

    # Test invalid level
    with pytest.raises(ValueError, match="level must be a non-negative integer"):
        LogTimer(logger, "test", -1)

    with pytest.raises(ValueError, match="level must be a non-negative integer"):
        LogTimer(logger, "test", "invalid_level")


def test_logtimer_context_with_exception(caplog):
    """Test LogTimer context manager when exception occurs."""
    logger = get_logger("timer_exception", caplog_friendly=True)

    with caplog.at_level(logging.ERROR):
        try:
            with LogTimer(logger, "Failing operation"):
                raise ValueError("Test error")
        except ValueError:
            pass  # Expected

    # Check error log was created
    error_logs = [r for r in caplog.records if r.levelno >= logging.ERROR]
    assert len(error_logs) >= 1
    assert "Failed: 'Failing operation'" in error_logs[0].getMessage()
    assert "ValueError: Test error" in error_logs[0].getMessage()


def test_logtimer_manual_start_stop():
    """Test LogTimer manual start/stop methods."""
    logger = get_logger("manual_timer", caplog_friendly=True)
    timer = LogTimer(logger, "Manual operation")

    # Test start
    timer.start()
    assert timer.start_time is not None

    # Test elapsed while running
    time.sleep(0.01)
    elapsed = timer.elapsed()
    assert elapsed > 0

    # Test stop
    final_elapsed = timer.stop()
    assert final_elapsed > 0
    assert timer.start_time is None  # Reset after stop


def test_logtimer_start_already_running():
    """Test starting timer when already running."""
    logger = get_logger("running_timer", caplog_friendly=True)
    timer = LogTimer(logger, "Already running")

    timer.start()
    with pytest.raises(RuntimeError, match="Timer for 'Already running' is already running"):
        timer.start()


def test_logtimer_stop_not_started():
    """Test stopping timer when not started."""
    logger = get_logger("not_started_timer", caplog_friendly=True)
    timer = LogTimer(logger, "Not started")

    with pytest.raises(RuntimeError, match="Timer for 'Not started' was not started"):
        timer.stop()


def test_logtimer_exit_without_start(caplog):
    """Test __exit__ when timer was not properly started."""
    logger = get_logger("exit_test", caplog_friendly=True)
    timer = LogTimer(logger, "Exit test")

    # Call __exit__ without calling __enter__
    with caplog.at_level(logging.ERROR):
        timer.__exit__(None, None, None)

    error_logs = [r for r in caplog.records if r.levelno >= logging.ERROR]
    assert any("was not properly started" in r.getMessage() for r in error_logs)


def test_logtimer_elapsed_not_started():
    """Test elapsed method when timer not started."""
    logger = get_logger("elapsed_test", caplog_friendly=True)
    timer = LogTimer(logger, "Elapsed test")

    assert timer.elapsed() == 0.0


def test_logtimer_as_decorator_validation():
    """Test LogTimer.as_decorator validation."""
    # Test invalid logger
    with pytest.raises(TypeError, match="logger must be a logging.Logger instance"):
        LogTimer.as_decorator("not_a_logger")

    # Test invalid level
    logger = logging.getLogger("decorator_test")
    with pytest.raises(ValueError, match="level must be a non-negative integer"):
        LogTimer.as_decorator(logger, level=-1)


def test_logtimer_as_decorator_with_function_name():
    """Test decorator using function name when operation_name is None."""
    logger = get_logger("decorator_func_name", caplog_friendly=True)

    @LogTimer.as_decorator(logger)  # No operation_name provided
    def test_function():
        return "result"

    result = test_function()
    assert result == "result"


@patch("time.perf_counter")
def test_logtimer_timing_calculation_error(mock_time, caplog):
    """Test error handling during timing calculation."""
    logger = get_logger("timing_error", caplog_friendly=True)

    # Make perf_counter raise an exception on second call
    mock_time.side_effect = [100.0, Exception("Timing error")]

    timer = LogTimer(logger, "Error timing")
    timer.start()

    with caplog.at_level(logging.ERROR):
        elapsed = timer.stop()

    assert elapsed == 0.0
    error_logs = [r for r in caplog.records if r.levelno >= logging.ERROR]
    assert any("Error stopping timer" in r.getMessage() for r in error_logs)


@patch("time.perf_counter")
def test_logtimer_exit_timing_error(mock_time, caplog):
    """Test error handling in __exit__ during timing calculation."""
    logger = get_logger("exit_timing_error", caplog_friendly=True)

    # Make perf_counter raise an exception on second call
    mock_time.side_effect = [100.0, Exception("Exit timing error")]

    with caplog.at_level(logging.ERROR):
        with LogTimer(logger, "Exit timing error"):
            pass

    error_logs = [r for r in caplog.records if r.levelno >= logging.ERROR]
    assert any("Error calculating timing" in r.getMessage() for r in error_logs)


# ======== TESTES PARA LogMetrics ========


def test_logmetrics_timer_context():
    """Test LogMetrics timer as context manager."""
    logger = get_logger("metrics_timer", caplog_friendly=True)
    metrics = LogMetrics(logger)

    # Test timer context manager (if implemented)
    metrics.start("context_timer")
    time.sleep(0.01)
    elapsed = metrics.stop("context_timer")

    assert elapsed > 0
    assert "context_timer" in metrics.timers
    assert metrics.timers["context_timer"]["elapsed"] is not None


def test_logmetrics_stop_non_existent_timer():
    """Test stopping a timer that doesn't exist."""
    logger = get_logger("metrics_stop", caplog_friendly=True)
    metrics = LogMetrics(logger)

    # Should raise RuntimeError for non-existent timer
    with pytest.raises(RuntimeError, match="was not started"):
        metrics.stop("non_existent")


def test_logmetrics_log_specific_metrics():
    """Test logging specific metrics by name."""
    logger = get_logger("metrics_log", caplog_friendly=True)
    metrics = LogMetrics(logger)

    # Test logging counter
    metrics.increment("test_counter", 5)
    metrics.log("test_counter")

    # Test logging value
    metrics.set("test_value", "hello")
    metrics.log("test_value")

    # Test logging completed timer
    metrics.start("test_timer")
    time.sleep(0.01)
    metrics.stop("test_timer")
    metrics.log("test_timer")

    # Test logging non-existent metric - should raise ValueError
    with pytest.raises(ValueError, match="not found"):
        metrics.log("non_existent")


def test_logmetrics_log_with_override_value(caplog):
    """Test logging metric with override value."""
    logger = get_logger("metrics_override", caplog_friendly=True)
    metrics = LogMetrics(logger)

    with caplog.at_level(logging.INFO):
        metrics.log("custom_metric", "override_value")

    logs = [r.getMessage() for r in caplog.records]
    assert any("custom_metric" in log and "override_value" in log for log in logs)


def test_logmetrics_log_all_with_active_timers():
    """Test log_all with active (not stopped) timers."""
    logger = get_logger("metrics_active", caplog_friendly=True)
    metrics = LogMetrics(logger)

    # Start timer but don't stop it
    metrics.start("active_timer")
    time.sleep(0.01)

    # Add some other metrics
    metrics.increment("counter", 3)
    metrics.set("value", 42)

    metrics.log_all()  # Should handle active timer gracefully


# ======== TESTES PARA FORMATTERS ========


def test_colored_formatter_edge_cases():
    """Test ColoredFormatter edge cases."""
    # Test with custom format and date format
    custom_formatter = ColoredFormatter(
        fmt="%(levelname)s - %(message)s", datefmt="%H:%M:%S", style="%", use_colors=True
    )

    record = logging.LogRecord(
        "test", logging.CRITICAL, "test.py", 1, "Critical message", None, None
    )

    output = custom_formatter.format(record)
    assert "CRITICAL" in output
    assert "Critical message" in output


def test_json_formatter_with_extra_fields():
    """Test JSONFormatter with extra fields in LogRecord."""
    formatter = JSONFormatter()

    record = logging.LogRecord("test", logging.INFO, "test.py", 1, "Test message", None, None)

    # Add extra fields
    record.user_id = 12345
    record.action = "login"
    record.custom_field = {"nested": "data"}

    output = formatter.format(record)
    data = json.loads(output)

    assert data["user_id"] == 12345
    assert data["action"] == "login"
    assert data["custom_field"] == {"nested": "data"}


# ======== TESTES PARA SPARK INTEGRATION ========


@pytest.mark.skipif(not spark_available, reason="PySpark not available")
def test_log_spark_dataframe_count_error(caplog):
    """Test error handling when DataFrame.count() fails."""
    spark = SparkSession.builder.master("local[1]").appName("error_test").getOrCreate()
    logger = get_logger("spark_error", caplog_friendly=True)

    # Create a DataFrame
    df = spark.createDataFrame([(1, "test")], ["id", "name"])

    # Mock count() to raise an exception
    with patch.object(df, "count", side_effect=Exception("Count error")):
        with caplog.at_level(logging.ERROR):
            log_spark_dataframe_info(df, logger, "ErrorDF")

    spark.stop()


@pytest.mark.skipif(not spark_available, reason="PySpark not available")
def test_log_spark_dataframe_schema_error(caplog):
    """Test error handling when schema display fails."""
    spark = SparkSession.builder.master("local[1]").appName("schema_error").getOrCreate()
    logger = get_logger("spark_schema_error", caplog_friendly=True)

    df = spark.createDataFrame([(1, "test")], ["id", "name"])

    # Mock schema access to raise an exception
    with patch.object(df, "_jdf") as mock_jdf:
        mock_jdf.schema.return_value.treeString.side_effect = Exception("Schema error")
        with caplog.at_level(logging.ERROR):
            log_spark_dataframe_info(df, logger, "SchemaErrorDF", show_schema=True)

    spark.stop()


@pytest.mark.skipif(not spark_available, reason="PySpark not available")
def test_log_spark_dataframe_sample_error(caplog):
    """Test error handling when sample display fails."""
    spark = SparkSession.builder.master("local[1]").appName("sample_error").getOrCreate()
    logger = get_logger("spark_sample_error", caplog_friendly=True)

    df = spark.createDataFrame([(1, "test")], ["id", "name"])

    # Mock limit().toPandas() to raise an exception
    with patch.object(df, "limit") as mock_limit:
        mock_limit.return_value.toPandas.side_effect = Exception("Sample error")
        with caplog.at_level(logging.ERROR):
            log_spark_dataframe_info(df, logger, "SampleErrorDF", show_sample=True)

    spark.stop()


@pytest.mark.skipif(not spark_available, reason="PySpark not available")
def test_log_spark_dataframe_stats_error(caplog):
    """Test error handling when statistics computation fails."""
    spark = SparkSession.builder.master("local[1]").appName("stats_error").getOrCreate()
    logger = get_logger("spark_stats_error", caplog_friendly=True)

    df = spark.createDataFrame([(1, 2.5), (2, 3.5)], ["id", "value"])

    # Mock select().describe().toPandas() to raise an exception
    with patch.object(df, "select") as mock_select:
        mock_select.return_value.describe.return_value.toPandas.side_effect = Exception(
            "Stats error"
        )
        with caplog.at_level(logging.ERROR):
            log_spark_dataframe_info(df, logger, "StatsErrorDF")

    spark.stop()


# ======== TESTES PARA SETUP E CONFIGURAÇÃO ========


def test_configure_basic_logging_existing_handlers():
    """Test configure_basic_logging removes existing handlers."""
    # Add some handlers to root logger
    root_logger = logging.getLogger()
    initial_handler = logging.StreamHandler()
    root_logger.addHandler(initial_handler)

    # Configure basic logging
    returned_logger = configure_basic_logging()

    # Should have different handlers now
    assert len(returned_logger.handlers) >= 1
    assert initial_handler not in returned_logger.handlers


def test_setup_file_logging_with_custom_prefix(tmp_log_dir):
    """Test setup_file_logging with custom file prefix."""
    logger = setup_file_logging(
        logger_name="custom_prefix_test",
        log_dir=tmp_log_dir + os.sep,
        file_prefix="my_custom_prefix",
        add_console=False,
    )

    logger.info("Test message")
    logger.close()

    # Check if files were created (exact naming may vary)
    files = os.listdir(tmp_log_dir)
    assert len(files) > 0  # At least one file should be created


def test_setup_file_logging_utc_timezone(tmp_log_dir):
    """Test setup_file_logging with different timezone."""
    logger = setup_file_logging(
        logger_name="utc_test", log_dir=tmp_log_dir + os.sep, utc="UTC", add_console=False
    )

    logger.info("UTC timezone test")
    logger.close()


def test_get_logger_with_propagate_false():
    """Test get_logger with explicit propagate=False."""
    logger = get_logger("no_propagate", level=logging.DEBUG, propagate=False, caplog_friendly=False)

    assert logger.propagate is False


# ======== TESTES PARA HANDLERS ========


def test_create_file_handler_with_custom_formatter(tmp_log_dir):
    """Test create_file_handler with custom formatter."""
    log_file = os.path.join(tmp_log_dir, "custom_format.log")
    custom_formatter = logging.Formatter("CUSTOM: %(message)s")

    handler = create_file_handler(log_file=log_file, formatter=custom_formatter)

    assert handler.formatter == custom_formatter


def test_create_timed_file_handler_custom_params(tmp_log_dir):
    """Test create_timed_file_handler with custom parameters."""
    log_file = os.path.join(tmp_log_dir, "timed_custom.log")

    handler = create_timed_file_handler(
        log_file=log_file, when="H", interval=2, backup_count=3, level=logging.WARNING  # Hourly
    )

    assert handler.level == logging.WARNING
    # interval é convertido para segundos (2 horas = 7200 segundos)
    assert handler.interval == 7200  # 2 * 60 * 60
    assert handler.backupCount == 3


def test_create_console_handler_with_custom_formatter():
    """Test create_console_handler with custom formatter."""
    custom_formatter = logging.Formatter("CONSOLE: %(message)s")

    handler = create_console_handler(level=logging.WARNING, formatter=custom_formatter)

    assert handler.level == logging.WARNING
    assert handler.formatter == custom_formatter


# ======== TESTE DE INTEGRAÇÃO COMPLETA ========


def test_complete_logging_pipeline(tmp_log_dir):
    """Test complete logging pipeline with all components."""
    # Setup comprehensive logging
    logger = setup_file_logging(
        logger_name="complete_test",
        log_dir=tmp_log_dir + os.sep,
        level=logging.DEBUG,
        console_level=logging.INFO,
        rotation="size",
        max_bytes=1024,
        backup_count=2,
        json_format=False,
        add_console=True,
    )

    # Use LogTimer
    with LogTimer(logger, "Complete operation"):
        # Use LogMetrics
        metrics = LogMetrics(logger)
        metrics.increment("operations", 1)
        metrics.set("status", "testing")
        metrics.start("sub_operation")

        # Log various levels
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")

        time.sleep(0.01)
        metrics.stop("sub_operation")
        metrics.log_all()

    logger.close()

    # Verify files were created (extension may vary)
    files = os.listdir(tmp_log_dir)
    assert len(files) > 0  # At least one file should be created


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
