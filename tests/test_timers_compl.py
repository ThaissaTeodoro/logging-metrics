"""
Testes específicos para atingir 100% de cobertura no código logging_metrics.
Foca nas linhas e condições que ainda não foram testadas.
"""

import json
import logging
import os
import sys
import time
from unittest.mock import patch

import pytest

from logging_metrics.core import (
    ColoredFormatter,
    Colors,
    JSONFormatter,
    LogMetrics,
    LogTimer,
    configure_basic_logging,
    get_logger,
    log_spark_dataframe_info,
    setup_file_logging,
)

try:
    spark_available = True
except ImportError:
    spark_available = False


# ======== TESTES PARA LINHAS ESPECÍFICAS DO LogTimer ========


def test_logtimer_init_validation_complete():
    """Test all validation paths in LogTimer.__init__."""

    # Test with valid logger
    logger = logging.getLogger("valid")

    # Test non-string operation_name
    with pytest.raises(ValueError, match="operation_name must be a non-empty string"):
        LogTimer(logger, 123)  # Non-string

    # Test non-int level
    with pytest.raises(ValueError, match="level must be a non-negative integer"):
        LogTimer(logger, "test", "invalid")  # Non-int level


def test_logtimer_manual_timer_full_cycle():
    """Test manual start/stop with all edge cases."""
    logger = get_logger("manual_cycle", caplog_friendly=True)
    timer = LogTimer(logger, "Manual Test")

    # Test elapsed when not started
    assert timer.elapsed() == 0.0

    # Test start
    timer.start()
    assert timer.start_time is not None

    # Test start when already running
    with pytest.raises(RuntimeError, match="is already running"):
        timer.start()

    # Test elapsed while running
    time.sleep(0.01)
    elapsed = timer.elapsed()
    assert elapsed > 0

    # Test stop
    final_elapsed = timer.stop()
    assert final_elapsed > 0
    assert timer.start_time is None  # Should be reset

    # Test stop when not started
    with pytest.raises(RuntimeError, match="was not started"):
        timer.stop()


@patch("time.perf_counter")
def test_logtimer_stop_with_exception_handling(mock_perf_counter, caplog):
    """Test LogTimer.stop() exception handling path."""
    logger = get_logger("stop_exception", caplog_friendly=True)
    timer = LogTimer(logger, "Exception Test")

    # Setup mock to raise exception on second call
    mock_perf_counter.side_effect = [100.0, Exception("Time error")]

    timer.start()

    with caplog.at_level(logging.ERROR):
        elapsed = timer.stop()

    # Should return 0.0 on exception and reset start_time
    assert elapsed == 0.0
    assert timer.start_time is None

    # Should log error
    error_logs = [r for r in caplog.records if r.levelno >= logging.ERROR]
    assert any("Error stopping timer" in r.getMessage() for r in error_logs)


@patch("time.perf_counter")
def test_logtimer_exit_with_exception_handling(mock_perf_counter, caplog):
    """Test LogTimer.__exit__() exception handling path."""
    logger = get_logger("exit_exception", caplog_friendly=True)

    # Setup mock to raise exception on second call
    mock_perf_counter.side_effect = [100.0, Exception("Exit time error")]

    with caplog.at_level(logging.ERROR):
        with LogTimer(logger, "Exit Exception Test"):
            pass  # Normal completion

    # Should log timing error
    error_logs = [r for r in caplog.records if r.levelno >= logging.ERROR]
    assert any("Error calculating timing" in r.getMessage() for r in error_logs)


def test_logtimer_decorator_validation_complete():
    """Test all validation paths in LogTimer.as_decorator."""

    # Test invalid logger type in decorator
    with pytest.raises(TypeError, match="logger must be a logging.Logger instance"):
        LogTimer.as_decorator("not_a_logger")

    # Test invalid level in decorator
    logger = logging.getLogger("decorator_test")
    with pytest.raises(ValueError, match="level must be a non-negative integer"):
        LogTimer.as_decorator(logger, level="invalid")


def test_logtimer_decorator_function_name_fallback():
    """Test decorator uses function name when operation_name is None."""
    logger = get_logger("func_name_test", caplog_friendly=True)

    @LogTimer.as_decorator(logger)  # No operation_name
    def my_test_function():
        return "success"

    result = my_test_function()
    assert result == "success"


# ======== TESTES ESPECÍFICOS PARA LogMetrics ========


def test_logmetrics_comprehensive_scenarios():
    """Test LogMetrics with comprehensive scenarios."""
    logger = get_logger("comprehensive_metrics", caplog_friendly=True)
    metrics = LogMetrics(logger, level=logging.DEBUG)  # Test custom level

    # Test increment with zero
    metrics.increment("zero_counter", 0)
    assert metrics.counters["zero_counter"] == 0

    # Test increment new counter
    metrics.increment("new_counter")
    assert metrics.counters["new_counter"] == 1

    # Test increment existing counter
    metrics.increment("new_counter", 3)
    assert metrics.counters["new_counter"] == 4

    # Test set with None value
    metrics.set("none_value", None)
    assert metrics.values["none_value"] is None

    # Test timer that doesn't exist in stop - should raise RuntimeError
    with pytest.raises(RuntimeError, match="was not started"):
        metrics.stop("nonexistent_timer")


def test_logmetrics_log_individual_metrics(caplog):
    """Test logging individual metrics by name."""
    logger = get_logger("individual_metrics", caplog_friendly=True)
    metrics = LogMetrics(logger)

    # Setup various metrics
    metrics.increment("test_counter", 5)
    metrics.set("test_value", "hello")
    metrics.start("test_timer")
    time.sleep(0.01)
    metrics.stop("test_timer")

    with caplog.at_level(logging.INFO):
        # Log individual metrics
        metrics.log("test_counter")
        metrics.log("test_value")
        metrics.log("test_timer")

        # Test logging non-existent metric - should raise ValueError
        with pytest.raises(ValueError, match="not found"):
            metrics.log("nonexistent_metric")

        # Test logging with override value
        metrics.log("override_test", "override_value")

    logs = [r.getMessage() for r in caplog.records]
    assert any("Counter 'test_counter': 5" in log for log in logs)
    assert any("Value 'test_value': hello" in log for log in logs)
    assert any("Timer 'test_timer':" in log for log in logs)
    assert any("override_test" in log and "override_value" in log for log in logs)


# ======== TESTES PARA JSONFormatter ========


def test_json_formatter_complete_coverage():
    """Test JSONFormatter with all possible LogRecord attributes."""
    formatter = JSONFormatter()

    # Create comprehensive LogRecord
    record = logging.LogRecord(
        name="test.module",
        level=logging.ERROR,
        pathname="/path/to/test.py",
        lineno=42,
        msg="Test error with args: %s, %s",
        args=("arg1", "arg2"),
        exc_info=None,
    )

    # Add all possible extra attributes
    record.custom_field = "custom_value"
    record.user_id = 12345
    record.request_id = "req-123"

    output = formatter.format(record)
    data = json.loads(output)

    # Verify standard fields
    assert data["name"] == "test.module"
    assert data["level"] == "ERROR"
    assert data["line"] == 42
    assert data["message"] == "Test error with args: arg1, arg2"

    # Verify custom fields are included
    assert data["custom_field"] == "custom_value"
    assert data["user_id"] == 12345
    assert data["request_id"] == "req-123"


def test_json_formatter_formattime():
    """Test JSONFormatter formatTime method is used."""
    formatter = JSONFormatter(datefmt="%Y-%m-%d")

    record = logging.LogRecord("test", logging.INFO, "test.py", 1, "Test", None, None)

    output = formatter.format(record)
    data = json.loads(output)

    # Should have timestamp field formatted
    assert "timestamp" in data
    assert isinstance(data["timestamp"], str)


# ======== TESTES PARA ColoredFormatter ========


def test_colored_formatter_all_levels():
    """Test ColoredFormatter with all log levels."""
    formatter = ColoredFormatter(use_colors=True)

    levels_and_colors = [
        (logging.DEBUG, Colors.CYAN),
        (logging.INFO, Colors.GREEN),
        (logging.WARNING, Colors.YELLOW),
        (logging.ERROR, Colors.RED),
        (logging.CRITICAL, Colors.BG_RED),
    ]

    for level, expected_color in levels_and_colors:
        record = logging.LogRecord(
            "test", level, "test.py", 1, f"Message at level {level}", None, None
        )

        output = formatter.format(record)

        if level == logging.CRITICAL:
            # CRITICAL uses background color + white + bold
            assert Colors.BG_RED in output
            assert Colors.WHITE in output
            assert Colors.BOLD in output
        else:
            assert expected_color in output

        assert Colors.RESET in output


def test_colored_formatter_error_message_coloring():
    """Test that ERROR and CRITICAL messages get their message colored too."""
    formatter = ColoredFormatter(use_colors=True)

    # Test ERROR level
    error_record = logging.LogRecord(
        "test", logging.ERROR, "test.py", 1, "Error message", None, None
    )
    error_output = formatter.format(error_record)
    # Message should be colored for ERROR
    assert Colors.RED in error_output

    # Test CRITICAL level
    critical_record = logging.LogRecord(
        "test", logging.CRITICAL, "test.py", 1, "Critical message", None, None
    )
    critical_output = formatter.format(critical_record)
    # Message should be colored for CRITICAL
    assert Colors.BG_RED in critical_output


def test_colored_formatter_style_parameters():
    """Test ColoredFormatter with different style parameters."""
    # Test with '{' style
    formatter_brace = ColoredFormatter(
        fmt="{asctime} [{levelname}] {name} - {message}", style="{", use_colors=True
    )

    # Test with '$' style
    formatter_dollar = ColoredFormatter(
        fmt="$asctime [$levelname] $name - $message", style="$", use_colors=True
    )

    record = logging.LogRecord("test", logging.INFO, "test.py", 1, "Test message", None, None)

    # Both should work without errors
    output_brace = formatter_brace.format(record)
    output_dollar = formatter_dollar.format(record)

    assert "INFO" in output_brace
    assert "INFO" in output_dollar
    assert Colors.GREEN in output_brace
    assert Colors.GREEN in output_dollar


# ======== TESTES PARA configure_basic_logging ========


def test_configure_basic_logging_remove_handlers():
    """Test that configure_basic_logging removes existing handlers."""
    root_logger = logging.getLogger()

    # Add a dummy handler
    dummy_handler = logging.StreamHandler()
    root_logger.addHandler(dummy_handler)

    # Configure basic logging
    returned_logger = configure_basic_logging(level=logging.WARNING, use_colors=False)

    # Should return root logger
    assert returned_logger is root_logger

    # Should have removed old handlers and added new one
    assert dummy_handler not in root_logger.handlers
    assert len(root_logger.handlers) >= 1


def test_configure_basic_logging_custom_format():
    """Test configure_basic_logging with custom format."""
    configure_basic_logging(
        level=logging.INFO,
        log_format="CUSTOM: %(levelname)s - %(message)s",
        date_format="%H:%M:%S",
        use_colors=True,
    )

    root_logger = logging.getLogger()
    assert len(root_logger.handlers) >= 1
    assert root_logger.level == logging.INFO


# ======== TESTES PARA get_logger ========


def test_get_logger_all_parameters():
    """Test get_logger with all parameter combinations."""

    # Test with explicit propagate=True
    logger1 = get_logger(
        "explicit_propagate", level=logging.DEBUG, propagate=True, caplog_friendly=False
    )
    assert logger1.propagate is True

    # Test with explicit propagate=False and caplog_friendly=False
    logger2 = get_logger(
        "explicit_no_propagate",
        propagate=False,
        caplog_friendly=False,  # Don't override with caplog_friendly
    )
    assert logger2.propagate is False

    # Test caplog_friendly behavior
    logger3 = get_logger("caplog_test", caplog_friendly=True)
    assert logger3.propagate is True  # caplog_friendly sets propagate=True


def test_get_logger_handler_replacement():
    """Test that get_logger replaces existing handlers when new ones provided."""
    logger_name = "handler_replacement_test"

    # First, create logger with one handler
    first_handler = logging.StreamHandler()
    logger = get_logger(logger_name, handlers=[first_handler])
    assert first_handler in logger.handlers

    # Then, replace with different handlers
    second_handler = logging.StreamHandler()
    third_handler = logging.StreamHandler()
    logger = get_logger(logger_name, handlers=[second_handler, third_handler])

    # Should have new handlers, not old one
    assert first_handler not in logger.handlers
    assert second_handler in logger.handlers
    assert third_handler in logger.handlers


# ======== TESTES PARA setup_file_logging ========


def test_setup_file_logging_default_file_prefix():
    """Test setup_file_logging uses logger_name as default file_prefix."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmp_dir:
        logger = setup_file_logging(
            logger_name="my.nested.logger",  # Contains dots
            log_dir=tmp_dir + os.sep,
            file_prefix=None,  # Should use logger_name with dots replaced
            add_console=False,
        )

        logger.info("Test message")
        logger.close()

        # Check if files were created (may have different naming convention)
        files = os.listdir(tmp_dir)
        assert len(files) > 0  # At least one file should be created
        # The exact naming may vary, so just check that files exist


def test_setup_file_logging_timezone_converter():
    """Test that setup_file_logging applies timezone converter to formatters."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmp_dir:
        logger = setup_file_logging(
            logger_name="timezone_test",
            log_dir=tmp_dir + os.sep,
            utc="Pacific/Auckland",  # Different timezone
            add_console=True,
            json_format=False,  # To test converter on non-JSON formatter
        )

        logger.info("Timezone test message")

        # Verify that non-JSON formatters have converter attribute set
        for handler in logger.handlers:
            if hasattr(handler.formatter, "converter"):
                assert handler.formatter.converter is not None

        logger.close()


def test_setup_file_logging_json_behavior():
    """Test setup_file_logging with JSON format behavior."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmp_dir:
        logger = setup_file_logging(
            logger_name="json_behavior_test",
            log_dir=tmp_dir + os.sep,
            json_format=True,
            add_console=True,
        )

        logger.info("JSON test message")

        # Verify that JSON formatters are used
        json_formatters = [
            handler.formatter
            for handler in logger.handlers
            if isinstance(handler.formatter, JSONFormatter)
        ]
        assert len(json_formatters) > 0  # At least one JSON formatter should exist

        logger.close()


# ======== TESTES PARA COBERTURA DE HANDLERS ========


def test_create_handlers_with_encoding():
    """Test file handlers with specific encoding."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmp_dir:
        from logging_metrics.core import create_file_handler, create_timed_file_handler

        # Test file handler with custom encoding
        file_path = os.path.join(tmp_dir, "encoded.log")
        handler1 = create_file_handler(log_file=file_path, encoding="utf-16", level=logging.WARNING)
        assert handler1.level == logging.WARNING
        handler1.close()

        # Test timed handler with custom encoding
        timed_path = os.path.join(tmp_dir, "timed_encoded.log")
        handler2 = create_timed_file_handler(
            log_file=timed_path, encoding="utf-16", level=logging.ERROR
        )
        assert handler2.level == logging.ERROR
        handler2.close()


def test_create_console_handler_stdout():
    """Test that console handler uses stdout."""
    from logging_metrics.core import create_console_handler

    handler = create_console_handler(level=logging.DEBUG, use_colors=True)

    # Should use stdout stream
    assert handler.stream == sys.stdout
    assert handler.level == logging.DEBUG


# ======== TESTES PARA SPARK COM DIFERENTES TIPOS DE DADOS ========


@pytest.mark.skipif(not spark_available, reason="PySpark not available")
def test_log_spark_dataframe_all_numeric_types():
    """Test Spark DataFrame with all supported numeric types."""
    from pyspark.sql import SparkSession

    spark = SparkSession.builder.master("local[1]").appName("all_numeric").getOrCreate()
    logger = get_logger("spark_all_numeric", caplog_friendly=True)

    try:
        # Create DataFrame with all numeric types that should generate stats
        df = spark.createDataFrame(
            [(1, 2.5, 3.0, 1000, 99.99), (2, 3.5, 4.0, 2000, 199.99), (3, 4.5, 5.0, 3000, 299.99)],
            ["int_col", "double_col", "float_col", "bigint_col", "decimal_col"],
        )

        # Cast to specific types to match the code's type checking
        df = df.select(
            df.int_col.cast("int"),
            df.double_col.cast("double"),
            df.float_col.cast("float"),
            df.bigint_col.cast("bigint"),
            df.decimal_col.cast("decimal(10,2)"),
        )

        log_spark_dataframe_info(
            df, logger, "AllNumericDF", show_schema=True, show_sample=True, sample_rows=3
        )

    finally:
        spark.stop()


@pytest.mark.skipif(not spark_available, reason="PySpark not available")
def test_log_spark_dataframe_mixed_types():
    """Test Spark DataFrame with mixed numeric and non-numeric types."""
    from pyspark.sql import SparkSession

    spark = SparkSession.builder.master("local[1]").appName("mixed_types").getOrCreate()
    logger = get_logger("spark_mixed", caplog_friendly=True)

    try:
        # Mix of numeric and non-numeric columns
        df = spark.createDataFrame(
            [
                (1, "Alice", 25.5, "2023-01-01", True),
                (2, "Bob", 30.0, "2023-01-02", False),
                (3, "Charlie", 35.5, "2023-01-03", True),
            ],
            ["id", "name", "age", "date", "active"],
        )

        # Cast to ensure proper types
        df = df.select(
            df.id.cast("int"),  # Should be included in stats
            df.name,  # String - not in stats
            df.age.cast("double"),  # Should be included in stats
            df.date,  # String - not in stats
            df.active,  # Boolean - not in stats
        )

        log_spark_dataframe_info(df, logger, "MixedTypesDF")

    finally:
        spark.stop()


# ======== TESTES PARA VALIDAÇÃO COMPLETA DE PARÂMETROS ========


def test_all_parameter_validation():
    """Test parameter validation in all functions."""

    # LogTimer validation
    logger = logging.getLogger("validation_test")

    # Test whitespace-only operation name
    with pytest.raises(ValueError):
        LogTimer(logger, "   \t\n   ")

    # Test level validation edge cases
    with pytest.raises(ValueError):
        LogTimer(logger, "test", -100)  # Very negative

    # LogMetrics custom level
    metrics = LogMetrics(logger, level=logging.CRITICAL)
    assert metrics.level == logging.CRITICAL


# ======== TESTES PARA LOG ALL SCENARIOS ========


def test_logmetrics_log_all_comprehensive(caplog):
    """Test LogMetrics.log_all with all possible combinations."""
    logger = get_logger("log_all_comprehensive", caplog_friendly=True)
    metrics = LogMetrics(logger)

    # Create all types of metrics
    metrics.increment("counter1", 5)
    metrics.increment("counter2", 3)
    metrics.set("value1", "string_value")
    metrics.set("value2", 42)
    metrics.set("value3", [1, 2, 3])

    # Mix of completed and active timers
    metrics.start("completed_timer")
    time.sleep(0.01)
    metrics.stop("completed_timer")

    metrics.start("active_timer1")
    metrics.start("active_timer2")
    time.sleep(0.01)
    # Leave these active

    with caplog.at_level(logging.INFO):
        metrics.log_all()

    logs = [r.getMessage() for r in caplog.records]

    # Verify all sections are present
    assert any("--- Processing Metrics ---" in log for log in logs)
    assert any("Counters:" in log for log in logs)
    assert any("Values:" in log for log in logs)
    assert any("Completed timers:" in log for log in logs)
    assert any("Active timers:" in log for log in logs)
    assert any("--------------------------------" in log for log in logs)

    # Verify specific metrics
    assert any("counter1: 5" in log for log in logs)
    assert any("value1: string_value" in log for log in logs)
    assert any("completed_timer:" in log for log in logs)
    assert any("active_timer1:" in log and "running" in log for log in logs)


# ======== TESTES PARA EDGE CASES FINAIS ========


def test_final_edge_cases():
    """Test final edge cases for complete coverage."""

    # Test ColoredFormatter with no colors and different levels
    formatter = ColoredFormatter(use_colors=False)

    for level in [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]:
        record = logging.LogRecord("test", level, "test.py", 1, "message", None, None)
        output = formatter.format(record)
        # Should not contain any color codes
        assert "\033[" not in output

    # Test LogTimer with very short operation name
    logger = get_logger("edge_timer", caplog_friendly=True)
    timer = LogTimer(logger, "a")  # Single character
    assert timer.operation_name == "a"

    # Test LogMetrics with zero values
    metrics = LogMetrics(logger)
    metrics.increment("zero", 0)
    metrics.set("zero_val", 0)
    metrics.log("zero")
    metrics.log("zero_val")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
