"""
Comprehensive test suite for logging-metrics v1.0.0.

This test suite covers all public API functionality including error handling,
edge cases, and integration scenarios. Tests are organized to validate both
the modular structure and backward compatibility.
"""

import json
import logging
import sys
import time
from logging.handlers import TimedRotatingFileHandler

import pytest

# Test main package imports
from logging_metrics import (
    __version__,
    __version_info__,
    get_version,
    get_version_info,
)

# Test backward compatibility
from logging_metrics.core import (
    ColoredFormatter as CoreColoredFormatter,
)
from logging_metrics.core import (
    LogMetrics as CoreLogMetrics,
)
from logging_metrics.core import (
    LogTimer as CoreLogTimer,
)

# Test both modular structure and backward compatibility
from logging_metrics.logger import (
    ColoredFormatter,
    Colors,
    JSONFormatter,
    _make_timezone_converter,
    configure_basic_logging,
    create_console_handler,
    create_file_handler,
    create_timed_file_handler,
    get_logger,
    log_spark_dataframe_info,
    setup_file_logging,
)
from logging_metrics.metrics import LogMetrics, TimerContext
from logging_metrics.timers import LogTimer

# Optional PySpark imports
try:
    from pyspark.sql import SparkSession

    spark_available = True
except ImportError:
    spark_available = False


class TestVersioning:
    """Test version information and API stability."""

    def test_version_format(self):
        """Test that version follows semantic versioning."""
        assert isinstance(__version__, str)
        assert len(__version__.split(".")) == 3
        assert __version__ == "1.0.0"

    def test_version_info_tuple(self):
        """Test version info tuple format."""
        assert isinstance(__version_info__, tuple)
        assert len(__version_info__) == 3
        assert __version_info__ == (1, 0, 0)

    def test_version_functions(self):
        """Test version utility functions."""
        assert get_version() == __version__
        assert get_version_info() == __version_info__


class TestBackwardCompatibility:
    """Test that all imports work for backward compatibility."""

    def test_modular_imports_work(self):
        """Test that modular imports are available."""
        assert Colors is not None
        assert ColoredFormatter is not None
        assert LogTimer is not None
        assert LogMetrics is not None

    def test_core_imports_identical(self):
        """Test that core imports are identical to modular ones."""
        assert ColoredFormatter is CoreColoredFormatter
        assert LogTimer is CoreLogTimer
        assert LogMetrics is CoreLogMetrics

    def test_main_package_imports(self):
        """Test that main package imports work."""
        from logging_metrics import ColoredFormatter, LogMetrics, LogTimer, setup_file_logging

        assert setup_file_logging is not None
        assert LogTimer is not None
        assert LogMetrics is not None
        assert ColoredFormatter is not None


class TestColoredFormatter:
    """Test ColoredFormatter functionality and error handling."""

    def test_initialization_with_defaults(self):
        """Test formatter initialization with default parameters."""
        formatter = ColoredFormatter()
        assert formatter.use_colors is True
        assert "%(asctime)s" in formatter._fmt

    def test_initialization_with_custom_params(self):
        """Test formatter initialization with custom parameters."""
        formatter = ColoredFormatter(fmt="%(message)s", datefmt="%H:%M:%S", use_colors=False)
        assert formatter.use_colors is False
        assert formatter._fmt == "%(message)s"

    def test_invalid_style_raises_error(self):
        """Test that invalid style parameter raises ValueError."""
        with pytest.raises(ValueError, match="Invalid style"):
            ColoredFormatter(style="invalid")

    def test_format_with_colors(self):
        """Test formatting with colors enabled."""
        record = logging.LogRecord("test", logging.WARNING, "path", 1, "test message", None, None)
        formatter = ColoredFormatter(use_colors=True)
        output = formatter.format(record)
        assert "\033[" in output  # Contains ANSI codes
        assert "WARNING" in output

    def test_format_without_colors(self):
        """Test formatting with colors disabled."""
        record = logging.LogRecord("test", logging.ERROR, "path", 1, "error message", None, None)
        formatter = ColoredFormatter(use_colors=False)
        output = formatter.format(record)
        assert "\033[" not in output  # No ANSI codes
        assert "ERROR" in output

    def test_format_invalid_record_type(self):
        """Test that invalid record type raises TypeError."""
        formatter = ColoredFormatter()
        with pytest.raises(TypeError, match="must be a logging.LogRecord"):
            formatter.format("not a record")

    def test_attribute_restoration(self):
        """Test that original record attributes are restored."""
        record = logging.LogRecord("test", logging.INFO, "path", 1, "test", None, None)
        original_levelname = record.levelname
        original_msg = record.msg

        formatter = ColoredFormatter(use_colors=True)
        formatter.format(record)

        assert record.levelname == original_levelname
        assert record.msg == original_msg


class TestJSONFormatter:
    """Test JSONFormatter functionality and error handling."""

    def test_initialization(self):
        """Test JSON formatter initialization."""
        formatter = JSONFormatter()
        assert formatter is not None

    def test_basic_json_format(self):
        """Test basic JSON formatting."""
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname=__file__,
            lineno=123,
            msg="Test message",
            args=None,
            exc_info=None,
            func="test_func",
        )
        formatter = JSONFormatter()
        output = formatter.format(record)

        # Parse JSON to verify structure
        data = json.loads(output)
        assert data["level"] == "INFO"
        assert data["name"] == "test_logger"
        assert data["message"] == "Test message"
        assert "timestamp" in data

    def test_json_format_with_exception(self):
        """Test JSON formatting with exception information."""
        try:
            raise ValueError("Test error")
        except ValueError:
            record = logging.LogRecord(
                "test",
                logging.ERROR,
                __file__,
                88,
                "Error occurred",
                None,
                sys.exc_info(),
                func="test_func",
            )
            formatter = JSONFormatter()
            output = formatter.format(record)

            data = json.loads(output)
            assert "exception" in data
            assert "ValueError" in data["exception"]["type"]
            assert "Test error" in data["exception"]["message"]

    def test_json_format_with_extra_data(self):
        """Test JSON formatting with extra log data."""
        record = logging.LogRecord("test", logging.INFO, __file__, 1, "Test", None, None)
        record.user_id = 12345
        record.action = "login"

        formatter = JSONFormatter()
        output = formatter.format(record)

        data = json.loads(output)
        assert data["user_id"] == 12345
        assert data["action"] == "login"

    def test_invalid_record_type(self):
        """Test that invalid record type raises TypeError."""
        formatter = JSONFormatter()
        with pytest.raises(TypeError, match="must be a logging.LogRecord"):
            formatter.format("not a record")

    def test_json_serialization_fallback(self):
        """Test fallback for non-serializable extra data."""
        record = logging.LogRecord("test", logging.INFO, __file__, 1, "Test", None, None)
        # Add non-serializable object
        record.complex_object = object()

        formatter = JSONFormatter()
        output = formatter.format(record)

        data = json.loads(output)
        assert "complex_object" in data
        assert isinstance(data["complex_object"], str)


class TestFileHandlers:
    """Test file handler creation and error handling."""

    def test_create_file_handler_success(self, tmp_path):
        """Test successful file handler creation."""
        log_file = tmp_path / "test.log"
        handler = create_file_handler(log_file=log_file, max_bytes=1024, backup_count=3)

        assert handler is not None
        assert handler.maxBytes == 1024
        assert handler.backupCount == 3
        assert handler.level == logging.DEBUG

    def test_create_file_handler_invalid_max_bytes(self):
        """Test file handler creation with invalid max_bytes."""
        with pytest.raises(ValueError, match="max_bytes must be positive"):
            create_file_handler("test.log", max_bytes=0)

        with pytest.raises(ValueError, match="max_bytes must be positive"):
            create_file_handler("test.log", max_bytes=-1)

    def test_create_file_handler_invalid_backup_count(self):
        """Test file handler creation with invalid backup_count."""
        with pytest.raises(ValueError, match="backup_count must be non-negative"):
            create_file_handler("test.log", backup_count=-1)

    def test_create_timed_file_handler_success(self, tmp_path):
        """Test successful timed file handler creation."""
        log_file = tmp_path / "timed.log"
        handler = create_timed_file_handler(log_file=log_file, when="H", interval=2, backup_count=5)

        assert handler is not None
        assert handler.when == "H"
        # O TimedRotatingFileHandler converte interval para segundos internamente
        # Para when="H" e interval=2, o resultado é 2 * 3600 = 7200 segundos
        assert handler.interval == 7200  # 2 horas em segundos
        assert handler.backupCount == 5
        assert isinstance(handler, TimedRotatingFileHandler)

    # Alternativa: teste com diferentes valores de when para verificar a conversão
    def test_create_timed_file_handler_intervals(self, tmp_path):
        """Test timed file handler with different interval types."""
        log_file = tmp_path / "timed_test.log"

        # Teste com segundos
        handler_s = create_timed_file_handler(log_file=log_file, when="S", interval=30)
        assert handler_s.interval == 30  # Segundos permanecem inalterados

        # Teste com minutos
        handler_m = create_timed_file_handler(log_file=log_file, when="M", interval=5)
        assert handler_m.interval == 300  # 5 minutos = 300 segundos

        # Teste com horas
        handler_h = create_timed_file_handler(log_file=log_file, when="H", interval=1)
        assert handler_h.interval == 3600  # 1 hora = 3600 segundos

        # Teste com dias
        handler_d = create_timed_file_handler(log_file=log_file, when="D", interval=1)
        assert handler_d.interval == 86400  # 1 dia = 86400 segundos

    def test_create_timed_file_handler_invalid_when(self):
        """Test timed handler creation with invalid 'when' parameter."""
        with pytest.raises(ValueError, match="Invalid 'when' value"):
            create_timed_file_handler("test.log", when="INVALID")

    def test_create_timed_file_handler_invalid_interval(self):
        """Test timed handler creation with invalid interval."""
        with pytest.raises(ValueError, match="interval must be positive"):
            create_timed_file_handler("test.log", interval=0)


class TestConsoleHandler:
    """Test console handler creation and error handling."""

    def test_create_console_handler_success(self):
        """Test successful console handler creation."""
        handler = create_console_handler(level=logging.WARNING, use_colors=False)

        assert handler is not None
        assert handler.level == logging.WARNING
        assert handler.stream == sys.stdout

    def test_create_console_handler_invalid_level(self):
        """Test console handler creation with invalid level."""
        with pytest.raises(ValueError, match="level must be a non-negative integer"):
            create_console_handler(level=-1)

        with pytest.raises(ValueError, match="level must be a non-negative integer"):
            create_console_handler(level="invalid")


class TestConfigureBasicLogging:
    """Test configure_basic_logging functionality and error handling."""

    def test_configure_basic_logging_default_params(self):
        """Test basic logging configuration with default parameters."""
        # Clear any existing handlers first
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        logger = configure_basic_logging()

        assert logger is not None
        assert isinstance(logger, logging.Logger)
        assert logger.level == logging.INFO
        assert len(logger.handlers) >= 1

        # Test that it's the root logger
        assert logger is root_logger

        # Test handler type
        handler = logger.handlers[0]
        assert isinstance(handler, logging.StreamHandler)
        assert isinstance(handler.formatter, ColoredFormatter)

        # Cleanup
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

    def test_configure_basic_logging_custom_level(self):
        """Test basic logging configuration with custom level."""
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        logger = configure_basic_logging(level=logging.DEBUG)

        assert logger.level == logging.DEBUG
        assert logger is root_logger

        # Cleanup
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

    def test_configure_basic_logging_custom_format(self):
        """Test basic logging configuration with custom format."""
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        custom_format = "%(levelname)s: %(message)s"
        logger = configure_basic_logging(
            level=logging.INFO, log_format=custom_format, use_colors=False
        )

        assert logger is not None
        assert logger is root_logger

        # Check that handler has the custom formatter
        handler = logger.handlers[0]
        assert isinstance(handler.formatter, ColoredFormatter)
        assert handler.formatter.use_colors is False

        # Cleanup
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

    def test_configure_basic_logging_with_colors(self):
        """Test basic logging configuration with colors enabled."""
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        logger = configure_basic_logging(use_colors=True)

        assert logger is not None
        assert len(logger.handlers) >= 1

        # Check that handler has ColoredFormatter
        handler = logger.handlers[0]
        assert isinstance(handler.formatter, ColoredFormatter)
        assert handler.formatter.use_colors is True

        # Cleanup
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

    def test_configure_basic_logging_without_colors(self):
        """Test basic logging configuration with colors disabled."""
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        logger = configure_basic_logging(use_colors=False)

        assert logger is not None
        assert len(logger.handlers) >= 1

        # Check that handler has ColoredFormatter with colors disabled
        handler = logger.handlers[0]
        assert isinstance(handler.formatter, ColoredFormatter)
        assert handler.formatter.use_colors is False

        # Cleanup
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

    def test_configure_basic_logging_removes_existing_handlers(self):
        """Test that configure_basic_logging removes existing handlers."""
        root_logger = logging.getLogger()

        # Add a dummy handler
        dummy_handler = logging.StreamHandler()
        root_logger.addHandler(dummy_handler)
        initial_handler_count = len(root_logger.handlers)
        assert initial_handler_count >= 1

        # Configure basic logging
        logger = configure_basic_logging()

        # Should have removed old handlers and added new ones
        assert logger is root_logger
        # Should have at least one handler (the new console handler)
        assert len(logger.handlers) >= 1

        # The dummy handler should be removed
        assert dummy_handler not in logger.handlers

        # Cleanup
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

    def test_configure_basic_logging_invalid_level(self):
        """Test configure_basic_logging with invalid level."""
        with pytest.raises(ValueError, match="level must be a non-negative integer"):
            configure_basic_logging(level=-1)

        with pytest.raises(ValueError, match="level must be a non-negative integer"):
            configure_basic_logging(level="invalid")

    def test_configure_basic_logging_custom_date_format(self):
        """Test basic logging configuration with custom date format."""
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        custom_date_format = "%H:%M:%S"
        logger = configure_basic_logging(
            date_format=custom_date_format, use_colors=False  # Easier to test without colors
        )

        assert logger is not None
        assert logger is root_logger

        # Check that handler was created
        assert len(logger.handlers) >= 1
        handler = logger.handlers[0]
        assert isinstance(handler.formatter, ColoredFormatter)

        # Cleanup
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

    def test_configure_basic_logging_handler_stream(self):
        """Test that console handler uses stdout."""
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        logger = configure_basic_logging()

        # Check that handler uses stdout
        handler = logger.handlers[0]
        assert isinstance(handler, logging.StreamHandler)
        assert handler.stream == sys.stdout

        # Cleanup
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

    """Test get_logger functionality and error handling."""

    def test_get_logger_basic(self):
        """Test basic logger creation."""
        logger = get_logger("test.logger")
        assert logger.name == "test.logger"
        assert isinstance(logger, logging.Logger)

    def test_get_logger_with_level(self):
        """Test logger creation with custom level."""
        logger = get_logger("test.logger", level=logging.WARNING)
        assert logger.level == logging.WARNING

    def test_get_logger_caplog_friendly(self):
        """Test caplog-friendly logger configuration."""
        logger = get_logger("test.caplog", caplog_friendly=True)
        assert logger.propagate is True
        assert len(logger.handlers) == 0

    def test_get_logger_with_handlers(self):
        """Test logger creation with custom handlers."""
        handler = logging.StreamHandler()
        logger = get_logger("test.handlers", handlers=[handler])
        assert handler in logger.handlers

    def test_get_logger_empty_name(self):
        """Test that empty name raises ValueError."""
        with pytest.raises(ValueError, match="name must be a non-empty string"):
            get_logger("")

        with pytest.raises(ValueError, match="name must be a non-empty string"):
            get_logger("   ")

    def test_get_logger_invalid_level(self):
        """Test that invalid level raises ValueError."""
        with pytest.raises(ValueError, match="level must be a non-negative integer"):
            get_logger("test", level=-1)

    def test_get_logger_invalid_handlers(self):
        """Test that invalid handlers raise TypeError."""
        with pytest.raises(TypeError, match="handlers must be a list"):
            get_logger("test", handlers="not a list")

        with pytest.raises(TypeError, match="must be a logging.Handler"):
            get_logger("test", handlers=["not a handler"])


class TestSetupFileLogging:
    """Test setup_file_logging functionality and error handling."""

    def test_setup_file_logging_basic(self, tmp_path):
        """Test basic file logging setup."""
        logger = setup_file_logging(
            logger_name="test_app", log_dir=str(tmp_path), add_console=False
        )

        assert logger.name == "test_app"
        assert hasattr(logger, "close")
        assert len(logger.handlers) >= 1

        # Test logging works
        logger.info("Test message")

        # Cleanup
        logger.close()

    def test_setup_file_logging_with_json(self, tmp_path):
        """Test file logging setup with JSON format."""
        logger = setup_file_logging(
            logger_name="json_app", log_dir=str(tmp_path), json_format=True, add_console=False
        )

        assert logger is not None
        logger.info("JSON test message")
        logger.close()

    def test_setup_file_logging_empty_name(self):
        """Test that empty logger name raises ValueError."""
        with pytest.raises(ValueError, match="logger_name must be a non-empty string"):
            setup_file_logging("")

    def test_setup_file_logging_invalid_rotation(self):
        """Test that invalid rotation type raises ValueError."""
        with pytest.raises(ValueError, match="rotation must be 'time' or 'size'"):
            setup_file_logging("test", rotation="invalid")

    def test_setup_file_logging_invalid_timezone(self):
        """Test that invalid timezone raises ValueError."""
        with pytest.raises(ValueError, match="Invalid timezone"):
            setup_file_logging("test", utc="Invalid/Timezone")
#--- logger final do logger

#--- test log timer
class TestLogTimer:
    """Test LogTimer functionality and error handling."""

    def test_logtimer_context_manager(self, caplog):
        """Test LogTimer as context manager."""
        logger = get_logger("timer_test", caplog_friendly=True)

        with caplog.at_level(logging.INFO):
            with LogTimer(logger, "Test operation"):
                time.sleep(0.01)

        messages = [record.getMessage() for record in caplog.records]
        assert any("Starting: Test operation" in msg for msg in messages)
        assert any("Completed: Test operation" in msg for msg in messages)

    def test_logtimer_decorator(self, caplog):
        """Test LogTimer as decorator."""
        logger = get_logger("timer_decorator", caplog_friendly=True)

        @LogTimer.as_decorator(logger, "Decorated function")
        def test_function():
            time.sleep(0.01)
            return "result"

        with caplog.at_level(logging.INFO):
            result = test_function()

        assert result == "result"
        messages = [record.getMessage() for record in caplog.records]
        assert any("Starting: Decorated function" in msg for msg in messages)
        assert any("Completed: Decorated function" in msg for msg in messages)

    def test_logtimer_decorator_uses_function_name(self, caplog):
        """Test that decorator uses function name when no operation name given."""
        logger = get_logger("timer_funcname", caplog_friendly=True)

        @LogTimer.as_decorator(logger)
        def my_function():
            return "done"

        with caplog.at_level(logging.INFO):
            my_function()

        messages = [record.getMessage() for record in caplog.records]
        assert any("Starting: my_function" in msg for msg in messages)

    def test_logtimer_manual_start_stop(self, caplog):
        """Test manual start/stop functionality."""
        logger = get_logger("timer_manual", caplog_friendly=True)
        timer = LogTimer(logger, "Manual operation")

        with caplog.at_level(logging.INFO):
            timer.start()
            time.sleep(0.01)
            elapsed = timer.stop()

        assert elapsed > 0
        messages = [record.getMessage() for record in caplog.records]
        assert any("Starting: Manual operation" in msg for msg in messages)
        assert any("Completed: Manual operation" in msg for msg in messages)

    def test_logtimer_elapsed_method(self):
        """Test elapsed time method."""
        logger = get_logger("timer_elapsed")
        timer = LogTimer(logger, "Elapsed test")

        # Before starting
        assert timer.elapsed() == 0.0

        # After starting
        timer.start()
        time.sleep(0.01)
        elapsed = timer.elapsed()
        assert elapsed > 0
        timer.stop()

    def test_logtimer_exception_handling(self, caplog):
        """Test LogTimer behavior when exception occurs."""
        logger = get_logger("timer_exception", caplog_friendly=True)

        with caplog.at_level(logging.ERROR):
            try:
                with LogTimer(logger, "Failing operation"):
                    raise ValueError("Test error")
            except ValueError:
                pass

        messages = [record.getMessage() for record in caplog.records]
        assert any("Failed: 'Failing operation'" in msg for msg in messages)
        assert any("ValueError: Test error" in msg for msg in messages)

    def test_logtimer_invalid_logger(self):
        """Test that invalid logger raises TypeError."""
        with pytest.raises(TypeError, match="logger must be a logging.Logger"):
            LogTimer("not a logger", "operation")

    def test_logtimer_empty_operation_name(self):
        """Test that empty operation name raises ValueError."""
        logger = get_logger("test")
        with pytest.raises(ValueError, match="operation_name must be a non-empty string"):
            LogTimer(logger, "")

    def test_logtimer_invalid_level(self):
        """Test that invalid level raises ValueError."""
        logger = get_logger("test")
        with pytest.raises(ValueError, match="level must be a non-negative integer"):
            LogTimer(logger, "operation", level=-1)

    def test_logtimer_double_start_error(self):
        """Test that starting already running timer raises RuntimeError."""
        logger = get_logger("test")
        timer = LogTimer(logger, "operation")

        timer.start()
        with pytest.raises(RuntimeError, match="Timer .* is already running"):
            timer.start()
        timer.stop()

    def test_logtimer_stop_not_started_error(self):
        """Test that stopping non-started timer raises RuntimeError."""
        logger = get_logger("test")
        timer = LogTimer(logger, "operation")

        with pytest.raises(RuntimeError, match="Timer .* was not started"):
            timer.stop()

    def test_logtimer_repr(self):
        """Test LogTimer string representation."""
        logger = get_logger("test")
        timer = LogTimer(logger, "test operation")

        repr_str = repr(timer)
        assert "LogTimer" in repr_str
        assert "test operation" in repr_str
        assert "stopped" in repr_str

        timer.start()
        repr_str = repr(timer)
        assert "running" in repr_str
        assert "elapsed=" in repr_str
        timer.stop()

#-metrics
class TestLogMetrics:
    """Test LogMetrics functionality and error handling."""

    def test_logmetrics_initialization(self):
        """Test LogMetrics initialization."""
        logger = get_logger("metrics_test")
        metrics = LogMetrics(logger)

        assert metrics.logger == logger
        assert metrics.level == logging.INFO
        assert len(metrics.counters) == 0
        assert len(metrics.values) == 0
        assert len(metrics.timers) == 0

    def test_logmetrics_invalid_logger(self):
        """Test that invalid logger raises TypeError."""
        with pytest.raises(TypeError, match="logger must be a logging.Logger"):
            LogMetrics("not a logger")

    def test_logmetrics_invalid_level(self):
        """Test that invalid level raises ValueError."""
        logger = get_logger("test")
        with pytest.raises(ValueError, match="level must be a non-negative integer"):
            LogMetrics(logger, level=-1)

    def test_increment_counter(self):
        """Test counter increment functionality."""
        logger = get_logger("test")
        metrics = LogMetrics(logger)

        metrics.increment("requests")
        assert metrics.get_counter("requests") == 1

        metrics.increment("requests", 5)
        assert metrics.get_counter("requests") == 6

        metrics.increment("requests", -2)
        assert metrics.get_counter("requests") == 4

    def test_increment_invalid_name(self):
        """Test that invalid metric name raises ValueError."""
        logger = get_logger("test")
        metrics = LogMetrics(logger)

        with pytest.raises(ValueError, match="metric_name must be a non-empty string"):
            metrics.increment("")

    def test_increment_invalid_value(self):
        """Test that invalid increment value raises TypeError."""
        logger = get_logger("test")
        metrics = LogMetrics(logger)

        with pytest.raises(TypeError, match="value must be an integer"):
            metrics.increment("counter", "not an int")

    def test_set_value(self):
        """Test value setting functionality."""
        logger = get_logger("test")
        metrics = LogMetrics(logger)

        metrics.set("status", "healthy")
        assert metrics.get_value("status") == "healthy"

        metrics.set("temperature", 23.5)
        assert metrics.get_value("temperature") == 23.5

        metrics.set("users", 1250)
        assert metrics.get_value("users") == 1250

    def test_set_invalid_name(self):
        """Test that invalid metric name raises ValueError."""
        logger = get_logger("test")
        metrics = LogMetrics(logger)

        with pytest.raises(ValueError, match="metric_name must be a non-empty string"):
            metrics.set("", "value")

    def test_timer_operations(self):
        """Test timer start/stop operations."""
        logger = get_logger("test")
        metrics = LogMetrics(logger)

        metrics.start("operation")
        time.sleep(0.01)
        elapsed = metrics.stop("operation")

        assert elapsed > 0
        assert metrics.get_timer_elapsed("operation") == elapsed

    def test_timer_context_manager(self):
        """Test timer context manager."""
        logger = get_logger("test")
        metrics = LogMetrics(logger)

        with metrics.timer("context_operation"):
            time.sleep(0.01)

        elapsed = metrics.get_timer_elapsed("context_operation")
        assert elapsed is not None
        assert elapsed > 0

    def test_timer_invalid_operations(self):
        """Test timer error conditions."""
        logger = get_logger("test")
        metrics = LogMetrics(logger)

        # Start with empty name
        with pytest.raises(ValueError, match="timer_name must be a non-empty string"):
            metrics.start("")

        # Stop non-existent timer
        with pytest.raises(RuntimeError, match="Timer .* was not started"):
            metrics.stop("nonexistent")

        # Start already running timer
        metrics.start("timer1")
        with pytest.raises(RuntimeError, match="Timer .* is already running"):
            metrics.start("timer1")

        # Stop already stopped timer
        metrics.stop("timer1")
        with pytest.raises(RuntimeError, match="Timer .* was already stopped"):
            metrics.stop("timer1")

    def test_get_summary(self):
        """Test get_summary functionality."""
        logger = get_logger("test")
        metrics = LogMetrics(logger)

        metrics.increment("requests", 10)
        metrics.set("status", "active")
        metrics.start("timer1")
        time.sleep(0.01)
        metrics.stop("timer1")
        metrics.start("timer2")  # Active timer

        summary = metrics.get_summary()

        assert summary["counters"]["requests"] == 10
        assert summary["values"]["status"] == "active"
        assert "timer1" in summary["completed_timers"]
        assert "timer2" in summary["active_timers"]
        assert summary["completed_timers"]["timer1"] > 0
        assert summary["active_timers"]["timer2"] > 0

    def test_reset_functionality(self):
        """Test reset functionality."""
        logger = get_logger("test")
        metrics = LogMetrics(logger)

        # Add some data
        metrics.increment("counter", 5)
        metrics.set("value", "test")
        metrics.start("timer")
        metrics.stop("timer")

        # Verify data exists
        assert len(metrics.counters) > 0
        assert len(metrics.values) > 0
        assert len(metrics.timers) > 0

        # Reset and verify empty
        metrics.reset()
        assert len(metrics.counters) == 0
        assert len(metrics.values) == 0
        assert len(metrics.timers) == 0

    def test_has_metric(self):
        """Test has_metric functionality."""
        logger = get_logger("test")
        metrics = LogMetrics(logger)

        assert not metrics.has_metric("nonexistent")

        metrics.increment("counter")
        assert metrics.has_metric("counter")

        metrics.set("value", "test")
        assert metrics.has_metric("value")

        metrics.start("timer")
        assert metrics.has_metric("timer")
        metrics.stop("timer")

    def test_list_metrics(self):
        """Test list_metrics functionality."""
        logger = get_logger("test")
        metrics = LogMetrics(logger)

        metrics.increment("counter1")
        metrics.increment("counter2")
        metrics.set("value1", "test")
        metrics.start("timer1")

        metric_names = metrics.list_metrics()

        assert "counter1" in metric_names["counters"]
        assert "counter2" in metric_names["counters"]
        assert "value1" in metric_names["values"]
        assert "timer1" in metric_names["timers"]

    def test_log_specific_metric(self, caplog):
        """Test logging specific metrics."""
        logger = get_logger("test", caplog_friendly=True)
        metrics = LogMetrics(logger)

        metrics.increment("requests", 100)
        metrics.set("status", "healthy")
        metrics.start("operation")
        time.sleep(0.01)
        metrics.stop("operation")

        with caplog.at_level(logging.INFO):
            metrics.log("requests")
            metrics.log("status")
            metrics.log("operation")
            metrics.log("custom", "custom_value")

        messages = [record.getMessage() for record in caplog.records]
        assert any("Counter 'requests': 100" in msg for msg in messages)
        assert any("Value 'status': healthy" in msg for msg in messages)
        assert any("Timer 'operation':" in msg for msg in messages)
        assert any("Metric 'custom': custom_value" in msg for msg in messages)

    def test_log_nonexistent_metric(self):
        """Test logging nonexistent metric raises ValueError."""
        logger = get_logger("test")
        metrics = LogMetrics(logger)

        with pytest.raises(ValueError, match="Metric .* not found"):
            metrics.log("nonexistent")

    def test_log_all_comprehensive(self, caplog):
        """Test comprehensive log_all functionality."""
        logger = get_logger("test", caplog_friendly=True)
        metrics = LogMetrics(logger)

        # Add various metrics
        metrics.increment("requests", 150)
        metrics.increment("errors", 3)
        metrics.set("status", "healthy")
        metrics.set("uptime", 3600)
        metrics.start("completed_op")
        time.sleep(0.01)
        metrics.stop("completed_op")
        metrics.start("active_op")  # Keep this running

        with caplog.at_level(logging.INFO):
            metrics.log_all()

        output = " ".join([record.getMessage() for record in caplog.records])

        assert "Processing Metrics" in output
        assert "Counters:" in output
        assert "requests: 150" in output
        assert "errors: 3" in output
        assert "Values:" in output
        assert "status: healthy" in output
        assert "uptime: 3600" in output
        assert "Completed timers:" in output
        assert "completed_op:" in output
        assert "Active timers:" in output
        assert "active_op:" in output
        assert "(running)" in output

    def test_repr(self):
        """Test LogMetrics string representation."""
        logger = get_logger("test")
        metrics = LogMetrics(logger)

        repr_str = repr(metrics)
        assert "LogMetrics" in repr_str
        assert "counters=0" in repr_str
        assert "timers=0" in repr_str

        # Add some metrics
        metrics.increment("counter")
        metrics.set("value", "test")
        metrics.start("timer1")
        metrics.stop("timer1")
        metrics.start("timer2")  # Active

        repr_str = repr(metrics)
        assert "counters=1" in repr_str
        assert "values=1" in repr_str
        assert "timers=2" in repr_str
        assert "1 completed, 1 active" in repr_str


#---- começa integração de timer
class TestTimerContext:
    """Test TimerContext functionality and error handling."""

    def test_timer_context_initialization(self):
        """Test TimerContext initialization."""
        logger = get_logger("test")
        metrics = LogMetrics(logger)
        context = TimerContext(metrics, "test_timer")

        assert context.metrics == metrics
        assert context.timer_name == "test_timer"

    def test_timer_context_invalid_metrics(self):
        """Test that invalid metrics raises TypeError."""
        with pytest.raises(TypeError, match="metrics must be a LogMetrics"):
            TimerContext("not metrics", "timer")

    def test_timer_context_empty_name(self):
        """Test that empty timer name raises ValueError."""
        logger = get_logger("test")
        metrics = LogMetrics(logger)

        with pytest.raises(ValueError, match="timer_name must be a non-empty string"):
            TimerContext(metrics, "")

    def test_timer_context_usage(self):
        """Test TimerContext in context manager."""
        logger = get_logger("test")
        metrics = LogMetrics(logger)

        with TimerContext(metrics, "context_test"):
            time.sleep(0.01)

        elapsed = metrics.get_timer_elapsed("context_test")
        assert elapsed is not None
        assert elapsed > 0


@pytest.mark.skipif(not spark_available, reason="PySpark not available")
class TestSparkIntegration:
    """Test PySpark DataFrame logging functionality."""

    @pytest.fixture
    def spark_session(self):
        """Create a test Spark session."""
        spark = SparkSession.builder.master("local[1]").appName("test").getOrCreate()
        yield spark
        spark.stop()

    def test_log_spark_dataframe_basic(self, spark_session, caplog):
        """Test basic DataFrame logging."""
        from pyspark.sql import Row

        logger = get_logger("spark_test", caplog_friendly=True)
        df = spark_session.createDataFrame(
            [Row(id=1, name="Alice", age=25), Row(id=2, name="Bob", age=30)]
        )

        with caplog.at_level(logging.INFO):
            log_spark_dataframe_info(
                df=df,
                logger=logger,
                name="test_df",
                show_schema=True,
                show_sample=True,
                sample_rows=2,
            )

        messages = [record.getMessage() for record in caplog.records]
        assert any("Row count: 2" in msg for msg in messages)
        assert any("Schema:" in msg for msg in messages)
        assert any("Sample data" in msg for msg in messages)

    def test_log_spark_dataframe_none(self, caplog):
        """Test logging None DataFrame."""
        logger = get_logger("spark_none", caplog_friendly=True)

        with caplog.at_level(logging.WARNING):
            log_spark_dataframe_info(None, logger, name="none_df")

        messages = [record.getMessage() for record in caplog.records]
        assert any("DataFrame is None" in msg for msg in messages)

    def test_log_spark_dataframe_invalid_logger(self, spark_session):
        """Test that invalid logger raises TypeError."""
        from pyspark.sql import Row

        df = spark_session.createDataFrame([Row(id=1)])

        with pytest.raises(TypeError, match="logger must be a logging.Logger"):
            log_spark_dataframe_info(df, "not a logger")

    def test_log_spark_dataframe_invalid_params(self, spark_session):
        """Test DataFrame logging with invalid parameters."""
        from pyspark.sql import Row

        logger = get_logger("test")
        df = spark_session.createDataFrame([Row(id=1)])

        with pytest.raises(ValueError, match="name must be a non-empty string"):
            log_spark_dataframe_info(df, logger, name="")

        with pytest.raises(ValueError, match="sample_rows must be positive"):
            log_spark_dataframe_info(df, logger, sample_rows=0)

        with pytest.raises(ValueError, match="log_level must be a non-negative integer"):
            log_spark_dataframe_info(df, logger, log_level=-1)


class TestTimezoneConverter:
    """Test timezone converter functionality."""

    def test_make_timezone_converter_valid(self):
        """Test timezone converter with valid timezone."""
        converter = _make_timezone_converter("UTC")
        timestamp = 1640995200.0  # 2022-01-01 00:00:00 UTC

        time_struct = converter(timestamp)
        assert hasattr(time_struct, "tm_year")
        assert time_struct.tm_year == 2022

    def test_make_timezone_converter_invalid_name(self):
        """Test timezone converter with invalid timezone name."""
        with pytest.raises(ValueError, match="tz_name must be a non-empty string"):
            _make_timezone_converter("")

        with pytest.raises(ValueError, match="Invalid timezone"):
            _make_timezone_converter("Invalid/Timezone")

    def test_make_timezone_converter_fallback(self):
        """Test timezone converter fallback behavior."""
        converter = _make_timezone_converter("UTC")

        # Test with invalid timestamp (should fallback gracefully)
        time_struct = converter(-1)  # Invalid timestamp
        assert hasattr(time_struct, "tm_year")


#-- integração 
class TestIntegrationScenarios:
    """Test integration scenarios and real-world usage patterns."""

    def test_complete_logging_workflow(self, tmp_path, caplog):
        """Test complete logging workflow from setup to cleanup."""
        # Setup file logging
        logger = setup_file_logging(
            logger_name="integration_test",
            log_dir=str(tmp_path),
            add_console=True,
            json_format=False,
        )

        # Use LogTimer
        with LogTimer(logger, "Integration test"):
            # Use LogMetrics
            metrics = LogMetrics(logger)

            # Simulate application workflow
            metrics.increment("startup_tasks", 3)
            metrics.set("environment", "test")

            with metrics.timer("database_setup"):
                time.sleep(0.01)  # Simulate DB setup

            with metrics.timer("data_processing"):
                for i in range(5):
                    metrics.increment("records_processed")
                    time.sleep(0.001)  # Simulate processing

            metrics.log_all()

        # Verify metrics
        summary = metrics.get_summary()
        assert summary["counters"]["startup_tasks"] == 3
        assert summary["counters"]["records_processed"] == 5
        assert summary["values"]["environment"] == "test"
        assert "database_setup" in summary["completed_timers"]
        assert "data_processing" in summary["completed_timers"]

        # Verify log files were created
        log_files = list(tmp_path.glob("**/*.log"))
        assert len(log_files) > 0

        # Cleanup
        logger.close()

    def test_error_recovery_scenarios(self, caplog):
        """Test error handling and recovery in various scenarios."""
        logger = get_logger("error_test", caplog_friendly=True)

        with caplog.at_level(logging.ERROR):
            # Test LogTimer with exception
            try:
                with LogTimer(logger, "Failing operation"):
                    raise RuntimeError("Simulated failure")
            except RuntimeError:
                pass

            # Test LogMetrics with invalid operations
            metrics = LogMetrics(logger)
            try:
                metrics.stop("nonexistent_timer")
            except RuntimeError:
                pass

            # Continue normal operations after errors
            metrics.increment("error_recoveries", 1)
            metrics.set("status", "recovered")

        # Verify recovery
        assert metrics.get_counter("error_recoveries") == 1
        assert metrics.get_value("status") == "recovered"

        # Check error messages were logged
        error_messages = [r.getMessage() for r in caplog.records if r.levelno >= logging.ERROR]
        assert len(error_messages) > 0
