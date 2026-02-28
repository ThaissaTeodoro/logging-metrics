import json
import logging
import os
import sys
import time
from unittest.mock import MagicMock

import pytest

from logging_metrics.core import (
    ColoredFormatter,
    Colors,
    JSONFormatter,
    LogMetrics,
    LogTimer,
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


# ======== TESTES ESPECÍFICOS PARA LINHAS NÃO COBERTAS ========


def test_logtimer_repr():
    """Test LogTimer __repr__ method."""
    logger = get_logger("repr_test", caplog_friendly=True)
    timer = LogTimer(logger, "Test Operation")

    # Test stopped state
    repr_stopped = repr(timer)
    assert "LogTimer(operation='Test Operation', status=stopped)" in repr_stopped

    # Test running state
    timer.start()
    time.sleep(0.01)
    repr_running = repr(timer)
    assert "LogTimer(operation='Test Operation', status=running" in repr_running
    assert "elapsed=" in repr_running

    timer.stop()


def test_colors_constants():
    """Test Colors class constants are defined."""
    # Test that all color constants exist and are strings
    assert isinstance(Colors.RESET, str)
    assert isinstance(Colors.BOLD, str)
    assert isinstance(Colors.RED, str)
    assert isinstance(Colors.GREEN, str)
    assert isinstance(Colors.YELLOW, str)
    assert isinstance(Colors.BLUE, str)
    assert isinstance(Colors.CYAN, str)
    assert isinstance(Colors.WHITE, str)
    assert isinstance(Colors.BG_RED, str)

    # Test that they contain ANSI escape sequences
    assert "\033[" in Colors.RED
    assert "\033[" in Colors.GREEN
    assert "\033[" in Colors.RESET


def test_colored_formatter_critical_level():
    """Test ColoredFormatter with CRITICAL level specifically."""
    formatter = ColoredFormatter(use_colors=True)

    record = logging.LogRecord("test", logging.CRITICAL, "test.py", 1, "Critical error", None, None)

    output = formatter.format(record)
    # Should contain background red and bold formatting for CRITICAL
    assert Colors.BG_RED in output
    assert Colors.WHITE in output
    assert Colors.BOLD in output


def test_colored_formatter_error_level_message_coloring():
    """Test that ERROR level messages get colored."""
    formatter = ColoredFormatter(use_colors=True)

    record = logging.LogRecord("test", logging.ERROR, "test.py", 1, "Error message", None, None)

    output = formatter.format(record)
    # Both levelname and message should be colored for ERROR
    assert Colors.RED in output


def test_json_formatter_with_stack_info():
    """Test JSONFormatter with stack_info."""
    formatter = JSONFormatter()

    record = logging.LogRecord("test", logging.INFO, "test.py", 1, "Test with stack", None, None)
    record.stack_info = "Stack trace here"

    output = formatter.format(record)
    data = json.loads(output)

    assert "message" in data
    assert data["message"] == "Test with stack"


def test_json_formatter_task_name():
    """Test JSONFormatter includes taskName if present."""
    formatter = JSONFormatter()

    record = logging.LogRecord("test", logging.INFO, "test.py", 1, "Task message", None, None)
    record.taskName = "my_task"

    output = formatter.format(record)
    data = json.loads(output)

    assert "taskName" in data  # This might be excluded, but let's test
    # Note: taskName is in the exclusion list, so it won't appear


def test_create_file_handler_directory_creation():
    """Test that create_file_handler creates directories."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create a nested path that doesn't exist
        nested_path = os.path.join(tmp_dir, "subdir", "logs", "test.log")

        handler = create_file_handler(log_file=nested_path)

        # Directory should be created
        assert os.path.exists(os.path.dirname(nested_path))

        handler.close()


def test_create_timed_file_handler_directory_creation():
    """Test that create_timed_file_handler creates directories."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmp_dir:
        nested_path = os.path.join(tmp_dir, "subdir", "logs", "timed.log")

        handler = create_timed_file_handler(log_file=nested_path)

        assert os.path.exists(os.path.dirname(nested_path))

        handler.close()


def test_logmetrics_increment_with_different_values():
    """Test LogMetrics increment with various values."""
    logger = get_logger("metrics_increment", caplog_friendly=True)
    metrics = LogMetrics(logger)

    # Test default increment (1)
    metrics.increment("counter1")
    assert metrics.counters["counter1"] == 1

    # Test increment by specific amount
    metrics.increment("counter1", 5)
    assert metrics.counters["counter1"] == 6

    # Test negative increment
    metrics.increment("counter2", -3)
    assert metrics.counters["counter2"] == -3


def test_logmetrics_start_timer_multiple():
    """Test starting multiple timers."""
    logger = get_logger("metrics_multiple", caplog_friendly=True)
    metrics = LogMetrics(logger)

    # Start multiple timers
    metrics.start("timer1")
    metrics.start("timer2")

    assert "timer1" in metrics.timers
    assert "timer2" in metrics.timers
    assert metrics.timers["timer1"]["start"] is not None
    assert metrics.timers["timer2"]["start"] is not None

    # Stop them
    elapsed1 = metrics.stop("timer1")
    elapsed2 = metrics.stop("timer2")

    assert elapsed1 >= 0
    assert elapsed2 >= 0


def test_logmetrics_set_various_types():
    """Test LogMetrics set with various data types."""
    logger = get_logger("metrics_set", caplog_friendly=True)
    metrics = LogMetrics(logger)

    # Test different value types
    metrics.set("string_val", "hello")
    metrics.set("int_val", 42)
    metrics.set("float_val", 3.14)
    metrics.set("bool_val", True)
    metrics.set("list_val", [1, 2, 3])
    metrics.set("dict_val", {"key": "value"})

    assert metrics.values["string_val"] == "hello"
    assert metrics.values["int_val"] == 42
    assert metrics.values["float_val"] == 3.14
    assert metrics.values["bool_val"] is True
    assert metrics.values["list_val"] == [1, 2, 3]
    assert metrics.values["dict_val"] == {"key": "value"}


@pytest.mark.skipif(not spark_available, reason="PySpark not available")
def test_log_spark_dataframe_with_numeric_stats():
    """Test Spark DataFrame logging with numeric columns for stats."""
    spark = SparkSession.builder.master("local[1]").appName("numeric_stats").getOrCreate()
    logger = get_logger("spark_numeric", caplog_friendly=True)

    # Create DataFrame with different numeric types
    df = spark.createDataFrame(
        [(1, 2.5, 100, 1000), (2, 3.5, 200, 2000), (3, 4.5, 300, 3000)],
        ["int_col", "double_col", "bigint_col", "long_col"],
    )

    # Change column types to match those checked in the code
    df = df.select(
        df.int_col.cast("int"),
        df.double_col.cast("double"),
        df.bigint_col.cast("bigint"),
        df.long_col.cast("long"),
    )

    log_spark_dataframe_info(
        df, logger, name="NumericDF", show_schema=True, show_sample=True, sample_rows=2
    )

    spark.stop()


@pytest.mark.skipif(not spark_available, reason="PySpark not available")
def test_log_spark_dataframe_no_numeric_columns():
    """Test Spark DataFrame logging with no numeric columns (no stats)."""
    spark = SparkSession.builder.master("local[1]").appName("no_numeric").getOrCreate()
    logger = get_logger("spark_no_numeric", caplog_friendly=True)

    # Create DataFrame with only string columns
    df = spark.createDataFrame(
        [("Alice", "Manager"), ("Bob", "Developer"), ("Charlie", "Analyst")], ["name", "role"]
    )

    log_spark_dataframe_info(df, logger, name="StringOnlyDF")

    spark.stop()


def test_setup_file_logging_with_all_options(tmp_log_dir):
    """Test setup_file_logging with all possible options."""
    logger = setup_file_logging(
        logger_name="full_options_test",
        log_folder="test_subfolder",
        log_dir=tmp_log_dir + os.sep,
        file_prefix="full_test",
        level=logging.DEBUG,
        console_level=logging.WARNING,
        rotation="size",
        max_bytes=2048,
        backup_count=3,
        add_console=True,
        use_colors=False,  # Test without colors
        log_format="CUSTOM: %(asctime)s - %(message)s",
        date_format="%Y-%m-%d %H:%M:%S",
        utc="Europe/London",
        json_format=False,
    )

    # Test logging at different levels
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")

    logger.close()

    # Verify subfolder was created
    subfolder_path = os.path.join(tmp_log_dir, "test_subfolder")
    assert os.path.exists(subfolder_path)

    # Verify log file was created with custom prefix
    files = os.listdir(subfolder_path)
    assert any("full_test" in f for f in files)


def test_setup_file_logging_time_rotation_all_params(tmp_log_dir):
    """Test setup_file_logging with time rotation and all parameters."""
    logger = setup_file_logging(
        logger_name="time_rotation_test",
        log_dir=tmp_log_dir + os.sep,
        rotation="time",  # Use time rotation
        backup_count=5,
        add_console=False,  # No console output
        json_format=True,  # JSON format
        utc="Asia/Tokyo",
    )

    logger.info("Time rotation test", extra={"test_field": "test_value"})
    logger.close()

    # Verify file was created (check any file, not specific extension)
    files = os.listdir(tmp_log_dir)
    assert len(files) > 0  # At least one file should be created


def test_get_logger_caplog_friendly_true():
    """Test get_logger with caplog_friendly=True removes handlers."""
    logger = get_logger("caplog_test", caplog_friendly=True)

    # Should have no handlers and propagate=True for caplog
    assert len(logger.handlers) == 0
    assert logger.propagate is True


def test_get_logger_caplog_friendly_false_with_handlers():
    """Test get_logger with caplog_friendly=False and custom handlers."""
    custom_handler = logging.StreamHandler()

    logger = get_logger(
        "custom_handlers_test", handlers=[custom_handler], caplog_friendly=False, propagate=False
    )

    assert custom_handler in logger.handlers
    assert logger.propagate is False


# ======== TESTES PARA CENÁRIOS DE ERRO ESPECÍFICOS ========


def test_logtimer_decorator_with_exception():
    """Test LogTimer decorator when decorated function raises exception."""
    logger = get_logger("decorator_exception", caplog_friendly=True)

    @LogTimer.as_decorator(logger, "Failing function")
    def failing_function():
        raise ValueError("Function failed")

    with pytest.raises(ValueError, match="Function failed"):
        failing_function()


def test_logtimer_context_manager_preserves_exception():
    """Test that LogTimer context manager preserves original exceptions."""
    logger = get_logger("context_exception", caplog_friendly=True)

    with pytest.raises(RuntimeError, match="Original error"):
        with LogTimer(logger, "Context operation"):
            raise RuntimeError("Original error")


def test_json_formatter_complex_exception():
    """Test JSONFormatter with complex exception including cause."""
    formatter = JSONFormatter()

    try:
        try:
            raise ValueError("Inner error")
        except ValueError as e:
            raise RuntimeError("Outer error") from e
    except RuntimeError:
        record = logging.LogRecord(
            "test", logging.ERROR, "test.py", 1, "Complex error", None, sys.exc_info()
        )

        output = formatter.format(record)
        data = json.loads(output)

        assert "exception" in data
        assert data["exception"]["type"] == "RuntimeError"
        assert "Outer error" in data["exception"]["message"]


def test_colored_formatter_unknown_level():
    """Test ColoredFormatter with unknown log level."""
    formatter = ColoredFormatter(use_colors=True)

    # Create record with non-standard level
    record = logging.LogRecord(
        "test",
        25,
        "test.py",
        1,
        "Custom level message",
        None,
        None,  # 25 is between INFO and WARNING
    )
    record.levelname = "CUSTOM"

    output = formatter.format(record)
    # Should still format without error, using default color (RESET)
    assert "CUSTOM" in output
    assert "Custom level message" in output


def test_logmetrics_timer_edge_cases():
    """Test LogMetrics timer edge cases."""
    logger = get_logger("timer_edge", caplog_friendly=True)
    metrics = LogMetrics(logger)

    # Test stopping timer that doesn't exist (should raise RuntimeError)
    with pytest.raises(RuntimeError, match="was not started"):
        metrics.stop("nonexistent_timer")

    # Test normal timer cycle
    metrics.start("normal_timer")
    time.sleep(0.01)
    elapsed = metrics.stop("normal_timer")
    assert elapsed > 0

    # Test log_all with active timer
    metrics.start("active_timer")
    time.sleep(0.01)
    # Don't stop this one - should appear as active in log_all
    metrics.log_all()


def test_setup_file_logging_close_method():
    """Test the close method added to logger."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmp_dir:
        logger = setup_file_logging(
            logger_name="close_test", log_dir=tmp_dir + os.sep, add_console=True
        )

        logger.info("Test message before close")

        # Test that logger has close method
        assert hasattr(logger, "close")
        assert callable(logger.close)

        # Test calling close
        logger.close()

        # Handlers should be removed
        assert len(logger.handlers) == 0


def test_setup_file_logging_close_method_with_error():
    """Test close method handles handler errors gracefully."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmp_dir:
        logger = setup_file_logging(logger_name="close_error_test", log_dir=tmp_dir + os.sep)

        # Mock a handler to raise exception on close
        mock_handler = MagicMock()
        mock_handler.close.side_effect = Exception("Close error")
        logger.addHandler(mock_handler)

        # Should not raise exception
        logger.close()


# ======== TESTES PARA COBERTURA DE LINHAS ESPECÍFICAS ========


def test_logmetrics_log_all_empty():
    """Test LogMetrics log_all with no metrics."""
    logger = get_logger("empty_metrics", caplog_friendly=True)
    metrics = LogMetrics(logger)

    # Should not crash with empty metrics
    metrics.log_all()


def test_logmetrics_log_all_only_counters(caplog):
    """Test LogMetrics log_all with only counters."""
    logger = get_logger("only_counters", caplog_friendly=True)
    metrics = LogMetrics(logger)

    metrics.increment("counter1", 5)
    metrics.increment("counter2", 3)

    with caplog.at_level(logging.INFO):
        metrics.log_all()

    logs = [r.getMessage() for r in caplog.records]
    assert any("Counters:" in log for log in logs)
    assert any("counter1: 5" in log for log in logs)
    assert any("counter2: 3" in log for log in logs)


def test_logmetrics_log_all_only_values(caplog):
    """Test LogMetrics log_all with only values."""
    logger = get_logger("only_values", caplog_friendly=True)
    metrics = LogMetrics(logger)

    metrics.set("value1", "test")
    metrics.set("value2", 42)

    with caplog.at_level(logging.INFO):
        metrics.log_all()

    logs = [r.getMessage() for r in caplog.records]
    assert any("Values:" in log for log in logs)
    assert any("value1: test" in log for log in logs)
    assert any("value2: 42" in log for log in logs)


def test_logmetrics_log_all_only_timers(caplog):
    """Test LogMetrics log_all with only completed timers."""
    logger = get_logger("only_timers", caplog_friendly=True)
    metrics = LogMetrics(logger)

    metrics.start("timer1")
    time.sleep(0.01)
    metrics.stop("timer1")

    with caplog.at_level(logging.INFO):
        metrics.log_all()

    logs = [r.getMessage() for r in caplog.records]
    assert any("Completed timers:" in log for log in logs)
    assert any("timer1:" in log for log in logs)


def test_logmetrics_log_all_mixed_timers(caplog):
    """Test LogMetrics log_all with both active and completed timers."""
    logger = get_logger("mixed_timers", caplog_friendly=True)
    metrics = LogMetrics(logger)

    # Completed timer
    metrics.start("completed_timer")
    time.sleep(0.01)
    metrics.stop("completed_timer")

    # Active timer
    metrics.start("active_timer")
    time.sleep(0.01)
    # Don't stop this one

    with caplog.at_level(logging.INFO):
        metrics.log_all()

    logs = [r.getMessage() for r in caplog.records]
    assert any("Completed timers:" in log for log in logs)
    assert any("Active timers:" in log for log in logs)
    assert any("completed_timer:" in log for log in logs)
    assert any("active_timer:" in log for log in logs)


# ======== TESTES DE INTEGRAÇÃO PARA CASOS ESPECÍFICOS ========


def test_full_pipeline_with_errors_and_recovery(tmp_log_dir, caplog):
    """Test complete pipeline with intentional errors and recovery."""
    logger = setup_file_logging(
        logger_name="error_recovery_test",
        log_dir=tmp_log_dir + os.sep,
        level=logging.DEBUG,
        console_level=logging.ERROR,  # Only errors to console
        add_console=True,
        json_format=False,
    )

    metrics = LogMetrics(logger)

    # Successful operation
    with LogTimer(logger, "Successful operation"):
        metrics.increment("successful_ops")
        metrics.set("last_status", "success")
        logger.info("Operation completed successfully")

    # Failed operation
    try:
        with LogTimer(logger, "Failed operation"):
            metrics.increment("failed_ops")
            raise Exception("Simulated failure")
    except Exception:
        metrics.increment("errors_handled")
        logger.error("Handled expected error")

    # Manual timer operations
    timer = LogTimer(logger, "Manual operation")
    timer.start()
    time.sleep(0.01)
    elapsed = timer.elapsed()
    assert elapsed > 0
    timer.stop()

    # Log all metrics
    metrics.log_all()

    logger.close()

    # Verify file creation
    files = os.listdir(tmp_log_dir)
    assert len(files) > 0


def test_spark_integration_comprehensive():
    """Comprehensive test of Spark integration if available."""
    if not spark_available:
        pytest.skip("PySpark not available")

    spark = SparkSession.builder.master("local[1]").appName("comprehensive").getOrCreate()
    logger = get_logger("spark_comprehensive", caplog_friendly=True)

    try:
        # Test with None DataFrame
        log_spark_dataframe_info(None, logger, "NullDF")

        # Test with empty DataFrame
        empty_df = spark.createDataFrame([], "id INT, name STRING")
        log_spark_dataframe_info(empty_df, logger, "EmptyDF", show_sample=True)

        # Test with complex DataFrame
        complex_df = spark.createDataFrame(
            [(1, "Alice", 25.5, True), (2, "Bob", 30.0, False), (3, "Charlie", 35.5, True)],
            ["id", "name", "age", "active"],
        )

        log_spark_dataframe_info(
            complex_df, logger, "ComplexDF", show_schema=True, show_sample=True, sample_rows=2
        )

    finally:
        spark.stop()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
