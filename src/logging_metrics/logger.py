"""
Logging configuration and management utilities.

This module provides comprehensive logging functionality including colored formatters,
file rotation handlers, console handlers, and integration with PySpark DataFrames.
All functions are designed for production use with robust error handling.
"""

import json
import logging
import os
import sys
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import Any, Callable, List, Optional, Union

import pytz

# Public API definition
__all__ = [
    "Colors",
    "ColoredFormatter",
    "JSONFormatter",
    "create_file_handler",
    "create_timed_file_handler",
    "create_console_handler",
    "configure_basic_logging",
    "get_logger",
    "setup_file_logging",
    "log_spark_dataframe_info",
]


def _make_timezone_converter(tz_name: str) -> Callable[[float], time.struct_time]:
    """
    Creates a timezone converter function for log timestamps.

    Args:
        tz_name: Timezone name (e.g., 'America/Sao_Paulo', 'UTC').

    Returns:
        A function that converts epoch timestamps to struct_time in the specified timezone.

    Raises:
        pytz.UnknownTimeZoneError: If the timezone name is invalid.

    Example:
        >>> converter = _make_timezone_converter('UTC')
        >>> time_struct = converter(1640995200.0)  # 2022-01-01 00:00:00 UTC
    """
    if not isinstance(tz_name, str) or not tz_name.strip():
        raise ValueError("tz_name must be a non-empty string")

    try:
        tz = pytz.timezone(tz_name)
    except pytz.UnknownTimeZoneError:
        raise ValueError(f"Invalid timezone '{tz_name}'")

    def converter(timestamp: float) -> time.struct_time:
        """Convert epoch timestamp to struct_time in the specified timezone."""
        try:
            dt = datetime.fromtimestamp(timestamp, tz)
            return dt.timetuple()
        except (ValueError, OSError):
            # Fallback to UTC if timestamp is invalid
            dt = datetime.fromtimestamp(timestamp, pytz.UTC)
            return dt.timetuple()

    return converter


class Colors:
    """
    ANSI color constants for terminal formatting.

    This class provides color codes for terminal output formatting. Colors are organized
    into text colors, background colors, and text styling options.

    Example:
        >>> print(f"{Colors.RED}Error message{Colors.RESET}")
        >>> print(f"{Colors.BOLD}{Colors.GREEN}Success{Colors.RESET}")
    """

    # Reset and styling
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    # Text colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"


class ColoredFormatter(logging.Formatter):
    """
    Custom logging formatter that adds ANSI colors to terminal output.

    This formatter automatically applies colors to log messages based on their severity level.
    Colors can be disabled for environments that don't support ANSI escape sequences.

    Color scheme:
        - DEBUG: Cyan
        - INFO: Green
        - WARNING: Yellow
        - ERROR: Red
        - CRITICAL: Red background with white bold text

    Args:
        fmt: Format string for log messages. Defaults to a standard format.
        datefmt: Date/time format string. Defaults to ISO-like format.
        style: Formatting style ('%', '{', or '$'). Defaults to '%'.
        use_colors: Whether to apply ANSI colors. Defaults to True.

    Example:
        >>> formatter = ColoredFormatter(use_colors=True)
        >>> handler = logging.StreamHandler()
        >>> handler.setFormatter(formatter)
        >>> logger.addHandler(handler)
    """

    # Log level to color mapping
    COLORS = {
        logging.DEBUG: Colors.CYAN,
        logging.INFO: Colors.GREEN,
        logging.WARNING: Colors.YELLOW,
        logging.ERROR: Colors.RED,
        logging.CRITICAL: Colors.BG_RED + Colors.WHITE + Colors.BOLD,
    }

    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        style: str = "%",
        use_colors: bool = True,
    ) -> None:
        """
        Initialize the colored formatter.

        Args:
            fmt: Format string for logs. If None, uses default format.
            datefmt: Date/time format string. If None, uses default format.
            style: Formatting style ('%', '{', or '$').
            use_colors: Whether to use ANSI colors.

        Raises:
            ValueError: If style is not one of '%', '{', or '$'.
        """
        if style not in ("%", "{", "$"):
            raise ValueError(f"Invalid style '{style}', must be one of: '%', '{{', '$'")

        if fmt is None:
            fmt = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
        if datefmt is None:
            datefmt = "%Y-%m-%d %H:%M:%S"

        super().__init__(fmt=fmt, datefmt=datefmt, style=style)
        self.use_colors = bool(use_colors)

    def format(self, record: logging.LogRecord) -> str:
        """
        Format a log record with appropriate colors.

        Args:
            record: The log record to format.

        Returns:
            The formatted log message string, with colors if enabled.
        """
        if not isinstance(record, logging.LogRecord):
            raise TypeError("record must be a logging.LogRecord instance")

        # Save original attributes to restore after formatting
        original_levelname = record.levelname
        original_msg = record.msg

        try:
            # Add color if enabled
            if self.use_colors:
                # Colorize log level
                color = self.COLORS.get(record.levelno, Colors.RESET)
                record.levelname = f"{color}{record.levelname}{Colors.RESET}"

                # Colorize message for ERROR and CRITICAL levels
                if record.levelno >= logging.ERROR:
                    record.msg = f"{color}{record.msg}{Colors.RESET}"

            # Format message
            formatted_message = super().format(record)

        finally:
            # Always restore original attributes
            record.levelname = original_levelname
            record.msg = original_msg

        return formatted_message


class JSONFormatter(logging.Formatter):
    """
    Logging formatter that outputs structured JSON logs.

    This formatter is ideal for log analysis tools, monitoring systems, and
    structured logging pipelines. It preserves all log record information
    in a machine-readable JSON format.

    Args:
        datefmt: Date/time format string. If None, uses ISO format.

    Example:
        >>> formatter = JSONFormatter()
        >>> handler = logging.FileHandler('app.json')
        >>> handler.setFormatter(formatter)
        >>> logger.addHandler(handler)
        >>> logger.info("User login", extra={"user_id": 123, "ip": "192.168.1.1"})
    """

    def __init__(self, datefmt: Optional[str] = None) -> None:
        """
        Initialize the JSON formatter.

        Args:
            datefmt: Date/time format string. If None, uses ISO format.
        """
        super().__init__(datefmt=datefmt)

    def format(self, record: logging.LogRecord) -> str:
        """
        Format a log record as JSON.

        Args:
            record: The log record to format.

        Returns:
            JSON string containing the log data.

        Raises:
            TypeError: If record is not a LogRecord instance.
        """
        if not isinstance(record, logging.LogRecord):
            raise TypeError("record must be a logging.LogRecord instance")

        try:
            log_data = {
                "timestamp": self.formatTime(record, self.datefmt),
                "level": record.levelname,
                "name": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
            }

            # Add exception info if present
            if record.exc_info:
                log_data["exception"] = {
                    "type": record.exc_info[0].__name__,
                    "message": str(record.exc_info[1]),
                    "traceback": self.formatException(record.exc_info),
                }

            # Add extra LogRecord data (excluding standard attributes)
            standard_attrs = {
                "args",
                "asctime",
                "created",
                "exc_info",
                "exc_text",
                "filename",
                "funcName",
                "id",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "msg",
                "name",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "stack_info",
                "thread",
                "threadName",
            }

            for key, value in record.__dict__.items():
                if key not in standard_attrs:
                    # Ensure value is JSON serializable
                    try:
                        json.dumps(value)
                        log_data[key] = value
                    except (TypeError, ValueError):
                        log_data[key] = str(value)

            return json.dumps(log_data, ensure_ascii=False)

        except Exception as e:
            # Fallback to basic format if JSON formatting fails
            fallback_data = {
                "timestamp": self.formatTime(record, self.datefmt),
                "level": record.levelname,
                "name": record.name,
                "message": f"JSON formatting error: {e}. Original: {record.getMessage()}",
                "formatting_error": True,
            }
            return json.dumps(fallback_data)


def create_file_handler(
    log_file: Union[str, Path],
    max_bytes: int = 10485760,
    backup_count: int = 5,
    encoding: str = "utf-8",
    formatter: Optional[logging.Formatter] = None,
    level: int = logging.DEBUG,
) -> RotatingFileHandler:
    """
    Create a file handler with size-based log rotation.

    Args:
        log_file: Path to the log file. Parent directories will be created if needed.
        max_bytes: Maximum file size in bytes before rotation. Defaults to 10MB.
        backup_count: Number of backup files to keep. Defaults to 5.
        encoding: Text encoding for log files. Defaults to 'utf-8'.
        formatter: Custom formatter instance. If None, creates a default formatter.
        level: Minimum log level to handle. Defaults to DEBUG.

    Returns:
        Configured RotatingFileHandler instance.

    Raises:
        ValueError: If max_bytes <= 0 or backup_count < 0.
        OSError: If unable to create log directory or file.
        PermissionError: If insufficient permissions for log directory.

    Example:
        >>> handler = create_file_handler(
        ...     log_file="./logs/app.log",
        ...     max_bytes=50*1024*1024,  # 50MB
        ...     backup_count=10
        ... )
        >>> logger.addHandler(handler)
    """
    # Validate arguments
    if max_bytes <= 0:
        raise ValueError(f"max_bytes must be positive, got {max_bytes}")
    if backup_count < 0:
        raise ValueError(f"backup_count must be non-negative, got {backup_count}")
    if not isinstance(level, int) or level < 0:
        raise ValueError(f"level must be a non-negative integer, got {level}")

    # Convert to Path object for better handling
    log_file = Path(log_file)

    try:
        # Create directory if it doesn't exist
        log_file.parent.mkdir(parents=True, exist_ok=True)

        # Test write permissions
        if log_file.parent.exists() and not os.access(log_file.parent, os.W_OK):
            raise PermissionError(f"No write permission for directory: {log_file.parent}")

    except OSError as e:
        raise OSError(f"Failed to create log directory {log_file.parent}: {e}")

    try:
        # Create handler with rotation
        handler = RotatingFileHandler(
            filename=str(log_file), maxBytes=max_bytes, backupCount=backup_count, encoding=encoding
        )

        handler.setLevel(level)

        # Set formatter
        if formatter is None:
            formatter = logging.Formatter(
                fmt="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        handler.setFormatter(formatter)

        return handler

    except Exception as e:
        raise OSError(f"Failed to create file handler for {log_file}: {e}")


def create_timed_file_handler(
    log_file: Union[str, Path],
    when: str = "midnight",
    interval: int = 1,
    backup_count: int = 7,
    encoding: str = "utf-8",
    formatter: Optional[logging.Formatter] = None,
    level: int = logging.DEBUG,
) -> TimedRotatingFileHandler:
    """
    Create a file handler with time-based log rotation.

    Args:
        log_file: Path to the log file. Parent directories will be created if needed.
        when: When to rotate logs. Options: 'S', 'M', 'H', 'D', 'W0'-'W6', 'midnight'.
        interval: Rotation interval (e.g., every 2 hours if when='H' and interval=2).
        backup_count: Number of backup files to keep. Defaults to 7.
        encoding: Text encoding for log files. Defaults to 'utf-8'.
        formatter: Custom formatter instance. If None, creates a default formatter.
        level: Minimum log level to handle. Defaults to DEBUG.

    Returns:
        Configured TimedRotatingFileHandler instance.

    Raises:
        ValueError: If when is invalid, interval <= 0, or backup_count < 0.
        OSError: If unable to create log directory or file.
        PermissionError: If insufficient permissions for log directory.

    Example:
        >>> handler = create_timed_file_handler(
        ...     log_file="./logs/app.log",
        ...     when="midnight",
        ...     backup_count=30  # Keep 30 days
        ... )
        >>> logger.addHandler(handler)
    """
    # Validate arguments
    valid_when = {"S", "M", "H", "D", "midnight"} | {f"W{i}" for i in range(7)}
    if when not in valid_when:
        raise ValueError(f"Invalid 'when' value '{when}'. Must be one of: {valid_when}")

    if interval <= 0:
        raise ValueError(f"interval must be positive, got {interval}")
    if backup_count < 0:
        raise ValueError(f"backup_count must be non-negative, got {backup_count}")
    if not isinstance(level, int) or level < 0:
        raise ValueError(f"level must be a non-negative integer, got {level}")

    # Convert to Path object
    log_file = Path(log_file)

    try:
        # Create directory if it doesn't exist
        log_file.parent.mkdir(parents=True, exist_ok=True)

        # Test write permissions
        if log_file.parent.exists() and not os.access(log_file.parent, os.W_OK):
            raise PermissionError(f"No write permission for directory: {log_file.parent}")

    except OSError as e:
        raise OSError(f"Failed to create log directory {log_file.parent}: {e}")

    try:
        # Create handler with time-based rotation
        handler = TimedRotatingFileHandler(
            filename=str(log_file),
            when=when,
            interval=interval,
            backupCount=backup_count,
            encoding=encoding,
        )

        handler.setLevel(level)

        # Set formatter
        if formatter is None:
            formatter = logging.Formatter(
                fmt="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        handler.setFormatter(formatter)

        return handler

    except Exception as e:
        raise OSError(f"Failed to create timed file handler for {log_file}: {e}")


def create_console_handler(
    level: int = logging.INFO,
    use_colors: bool = True,
    formatter: Optional[logging.Formatter] = None,
    stream: Optional[Any] = None,
) -> logging.StreamHandler:
    """
    Create a console handler with optional color support.

    Args:
        level: Minimum log level to handle. Defaults to INFO.
        use_colors: Whether to use colored output. Defaults to True.
        formatter: Custom formatter instance. If None, creates a ColoredFormatter.
        stream: Output stream. If None, uses sys.stdout.

    Returns:
        Configured StreamHandler instance.

    Raises:
        ValueError: If level is invalid.

    Example:
        >>> handler = create_console_handler(
        ...     level=logging.WARNING,
        ...     use_colors=False
        ... )
        >>> logger.addHandler(handler)
    """
    if not isinstance(level, int) or level < 0:
        raise ValueError(f"level must be a non-negative integer, got {level}")

    # Use stdout by default
    if stream is None:
        stream = sys.stdout

    try:
        handler = logging.StreamHandler(stream)
        handler.setLevel(level)

        # Set formatter
        if formatter is None:
            formatter = ColoredFormatter(use_colors=use_colors)
        handler.setFormatter(formatter)

        return handler

    except Exception as e:
        raise RuntimeError(f"Failed to create console handler: {e}")


def configure_basic_logging(
    level: int = logging.INFO,
    log_format: str = "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    date_format: str = "%Y-%m-%d %H:%M:%S",
    use_colors: bool = True,
) -> logging.Logger:
    """
    Configure basic logging for console output with color formatting.

    This function sets up the root logger with a colored console handler. It's ideal
    for simple applications and development environments.

    Args:
        level: Default log level for both logger and handler.
        log_format: Format string for log messages.
        date_format: Date/time format string.
        use_colors: Whether to use colored output.

    Returns:
        The configured root logger instance.

    Raises:
        ValueError: If level is invalid.

    Example:
        >>> logger = configure_basic_logging(level=logging.DEBUG)
        >>> logger.info("Application started")
        >>> logger.error("An error occurred")
    """
    if not isinstance(level, int) or level < 0:
        raise ValueError(f"level must be a non-negative integer, got {level}")

    # Remove existing handlers to avoid duplication
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    root_logger.setLevel(level)

    try:
        # Create and add console handler
        formatter = ColoredFormatter(fmt=log_format, datefmt=date_format, use_colors=use_colors)

        console_handler = create_console_handler(
            level=level, use_colors=use_colors, formatter=formatter
        )

        root_logger.addHandler(console_handler)

        return root_logger

    except Exception as e:
        raise RuntimeError(f"Failed to configure basic logging: {e}")


def get_logger(
    name: str,
    level: Optional[int] = None,
    handlers: Optional[List[logging.Handler]] = None,
    propagate: Optional[bool] = None,
    caplog_friendly: bool = False,
) -> logging.Logger:
    """
    Get or create a logger with flexible configuration.

    This function provides a flexible way to create loggers that work well in both
    production and testing environments. The caplog_friendly option is particularly
    useful for pytest integration.

    Args:
        name: Logger name. Should follow hierarchical naming (e.g., 'myapp.module').
        level: Log level. If None, inherits from parent logger.
        handlers: List of handlers to attach. If None, no handlers are added.
        propagate: Whether to propagate messages to parent loggers.
                  If None, determined by caplog_friendly.
        caplog_friendly: If True, configures logger for pytest caplog compatibility.

    Returns:
        Configured Logger instance.

    Raises:
        ValueError: If name is empty or handlers contain invalid objects.
        TypeError: If handlers is not a list or contains non-Handler objects.

    Example:
        >>> # Production logger with file handler
        >>> file_handler = create_file_handler('./logs/app.log')
        >>> logger = get_logger('myapp', handlers=[file_handler], level=logging.INFO)

        >>> # Test-friendly logger
        >>> test_logger = get_logger('myapp.test', caplog_friendly=True)
    """
    if not isinstance(name, str) or not name.strip():
        raise ValueError("name must be a non-empty string")

    if level is not None and (not isinstance(level, int) or level < 0):
        raise ValueError(f"level must be a non-negative integer or None, got {level}")

    if handlers is not None:
        if not isinstance(handlers, list):
            raise TypeError("handlers must be a list or None")

        for i, handler in enumerate(handlers):
            if not isinstance(handler, logging.Handler):
                raise TypeError(f"handlers[{i}] must be a logging.Handler instance")

    # Get logger instance
    logger = logging.getLogger(name)

    # Set propagate automatically if not specified
    if propagate is None:
        propagate = caplog_friendly

    # Set level if specified
    if level is not None:
        logger.setLevel(level)

    try:
        # Configure for pytest caplog compatibility
        if caplog_friendly:
            # Remove own handlers to avoid interference with caplog
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)
            logger.propagate = True  # Allow messages to reach root logger
        else:
            # Production configuration
            if handlers:
                # Remove existing handlers before adding new ones
                for handler in logger.handlers[:]:
                    logger.removeHandler(handler)

                # Add new handlers
                for handler in handlers:
                    logger.addHandler(handler)

            logger.propagate = propagate

        return logger

    except Exception as e:
        raise RuntimeError(f"Failed to configure logger '{name}': {e}")


def setup_file_logging(
    logger_name: str,
    log_folder: str = "unknown/",
    log_dir: str = "./logs/",
    file_prefix: Optional[str] = None,
    level: int = logging.DEBUG,
    console_level: int = logging.INFO,
    rotation: str = "time",
    max_bytes: int = 10485760,
    backup_count: int = 5,
    add_console: bool = True,
    use_colors: bool = True,
    log_format: str = "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    date_format: str = "%Y-%m-%d %H:%M:%S",
    utc: str = "America/Sao_Paulo",
    json_format: bool = False,
) -> logging.Logger:
    """
    Configure a comprehensive logger with file output and optional console output.

    This is the main configuration function for production logging setups. It creates
    a logger with file rotation, optional console output, timezone support, and both
    text and JSON formatting options.

    Args:
        logger_name: Name of the logger to create/configure.
        log_folder: Subfolder within log_dir for organizing logs.
        log_dir: Base directory for log files.
        file_prefix: Prefix for log filenames. If None, uses sanitized logger_name.
        level: Log level for file output.
        console_level: Log level for console output (if enabled).
        rotation: Type of rotation - 'time' or 'size'.
        max_bytes: Maximum file size for size-based rotation.
        backup_count: Number of backup files to retain.
        add_console: Whether to add console handler.
        use_colors: Whether to use colored console output.
        log_format: Format string for log messages (when not using JSON).
        date_format: Date/time format string.
        utc: Timezone name for timestamps.
        json_format: Whether to use JSON formatting for both file and console.

    Returns:
        Configured Logger instance with a 'close' method for cleanup.

    Raises:
        ValueError: If arguments are invalid.
        OSError: If unable to create log directories or files.
        PermissionError: If insufficient permissions for log operations.

    Example:
        >>> logger = setup_file_logging(
        ...     logger_name="myapp",
        ...     log_dir="./logs",
        ...     level=logging.DEBUG,
        ...     console_level=logging.INFO,
        ...     json_format=True
        ... )
        >>> logger.info("Application started", extra={"version": "1.0.0"})
        >>> logger.close()  # Cleanup when done
    """
    # Validate required arguments
    if not isinstance(logger_name, str) or not logger_name.strip():
        raise ValueError("logger_name must be a non-empty string")

    if not isinstance(log_folder, str):
        raise ValueError("log_folder must be a string")

    if not isinstance(log_dir, str) or not log_dir.strip():
        raise ValueError("log_dir must be a non-empty string")

    if not isinstance(level, int) or level < 0:
        raise ValueError(f"level must be a non-negative integer, got {level}")

    if not isinstance(console_level, int) or console_level < 0:
        raise ValueError(f"console_level must be a non-negative integer, got {console_level}")

    if rotation not in ("time", "size"):
        raise ValueError(f"rotation must be 'time' or 'size', got '{rotation}'")

    # Create full log directory path
    full_log_dir = Path(log_dir) / log_folder

    try:
        full_log_dir.mkdir(parents=True, exist_ok=True)

        # Test write permissions
        if not os.access(full_log_dir, os.W_OK):
            raise PermissionError(f"No write permission for log directory: {full_log_dir}")

    except OSError as e:
        raise OSError(f"Failed to create log directory {full_log_dir}: {e}")

    # Generate log filename
    if file_prefix is None:
        file_prefix = logger_name.replace(".", "_")

    # Sanitize file prefix
    file_prefix = "".join(c for c in file_prefix if c.isalnum() or c in "._-")
    if not file_prefix:
        file_prefix = "application"

    try:
        # Create timezone converter
        timezone_converter = _make_timezone_converter(utc)

        # Generate timestamped filename
        utc_tz = pytz.timezone(utc)
        timestamp = datetime.now(utc_tz).strftime("%Y%m%d_%H%M%S")

        # Choose file extension based on format
        extension = "json" if json_format else "log"
        log_file = full_log_dir / f"{timestamp}-{file_prefix}.{extension}"

    except Exception as e:
        raise ValueError(f"Failed to setup log file path: {e}")

    # Prepare formatters
    handlers = []

    try:
        # Choose formatter based on format preference
        if json_format:
            file_formatter = JSONFormatter(datefmt=date_format)
        else:
            file_formatter = logging.Formatter(fmt=log_format, datefmt=date_format)
            file_formatter.converter = timezone_converter

        # Create file handler based on rotation type
        if rotation.lower() == "time":
            file_handler = create_timed_file_handler(
                log_file=log_file,
                level=level,
                formatter=file_formatter,
                backup_count=backup_count,
            )
        else:  # size rotation
            file_handler = create_file_handler(
                log_file=log_file,
                max_bytes=max_bytes,
                backup_count=backup_count,
                level=level,
                formatter=file_formatter,
            )

        handlers.append(file_handler)

        # Add console handler if requested
        if add_console:
            if json_format:
                console_formatter = JSONFormatter(datefmt=date_format)
            else:
                console_formatter = ColoredFormatter(
                    fmt=log_format, datefmt=date_format, use_colors=use_colors
                )
                console_formatter.converter = timezone_converter

            console_handler = create_console_handler(
                level=console_level,
                use_colors=use_colors,
                formatter=console_formatter,
            )
            handlers.append(console_handler)

        # Create logger with handlers
        logger = get_logger(name=logger_name, level=level, handlers=handlers, propagate=False)

        logger.info(f"Logger '{logger_name}' configured successfully (json_format={json_format})")

        # Add cleanup method to logger
        def close() -> None:
            """Close and cleanup all logger handlers."""
            for handler in logger.handlers[:]:
                try:
                    handler.flush()
                    handler.close()
                except Exception as e:
                    print(f"Warning: Error closing handler: {e}", file=sys.stderr)
                finally:
                    logger.removeHandler(handler)

        logger.close = close

        return logger

    except Exception as e:
        # Cleanup any created handlers on failure
        for handler in handlers:
            try:
                handler.close()
            except Exception:
                pass
        raise RuntimeError(f"Failed to setup file logging for '{logger_name}': {e}")


def log_spark_dataframe_info(
    df: Any,
    logger: logging.Logger,
    name: str = "DataFrame",
    show_schema: bool = True,
    show_sample: bool = False,
    sample_rows: int = 5,
    log_level: int = logging.INFO,
) -> None:
    """
    Log comprehensive information about a PySpark DataFrame.

    This function provides detailed logging of DataFrame properties including row count,
    schema, sample data, and statistical summaries. It's designed to be safe and
    handle various error conditions gracefully.

    Args:
        df: PySpark DataFrame to analyze. Can be None (will log warning).
        logger: Logger instance to use for output.
        name: Descriptive name for the DataFrame (used in log messages).
        show_schema: Whether to log the DataFrame schema.
        show_sample: Whether to log sample data rows.
        sample_rows: Number of sample rows to display (if show_sample=True).
        log_level: Log level to use for informational messages.

    Raises:
        ValueError: If sample_rows <= 0 or log_level is invalid.
        TypeError: If logger is not a Logger instance.

    Example:
        >>> from pyspark.sql import SparkSession
        >>> spark = SparkSession.builder.getOrCreate()
        >>> df = spark.createDataFrame([(1, "Alice"), (2, "Bob")], ["id", "name"])
        >>> log_spark_dataframe_info(
        ...     df=df,
        ...     logger=logger,
        ...     name="users_table",
        ...     show_schema=True,
        ...     show_sample=True,
        ...     sample_rows=3
        ... )

    Note:
        This function requires PySpark to be available. It gracefully handles
        cases where the DataFrame is None or operations fail due to Spark issues.
    """
    # Validate arguments
    if not isinstance(logger, logging.Logger):
        raise TypeError("logger must be a logging.Logger instance")

    if not isinstance(name, str) or not name.strip():
        raise ValueError("name must be a non-empty string")

    if sample_rows <= 0:
        raise ValueError(f"sample_rows must be positive, got {sample_rows}")

    if not isinstance(log_level, int) or log_level < 0:
        raise ValueError(f"log_level must be a non-negative integer, got {log_level}")

    # Handle None DataFrame
    if df is None:
        logger.warning(f"[{name}] DataFrame is None - no information to log")
        return

    try:
        # Try to get row count
        try:
            row_count = df.count()
            logger.log(log_level, f"[{name}] Row count: {row_count:,}")
        except Exception as e:
            logger.error(f"[{name}] Failed to count rows: {e}")

        # Show schema if requested
        if show_schema:
            try:
                # Check if DataFrame has the _jdf attribute (PySpark DataFrame)
                if hasattr(df, "_jdf") and hasattr(df._jdf, "schema"):
                    schema_str = df._jdf.schema().treeString()
                    logger.log(log_level, f"[{name}] Schema:\n{schema_str}")
                elif hasattr(df, "printSchema"):
                    # Alternative method for getting schema
                    import io
                    import sys

                    # Capture schema output
                    old_stdout = sys.stdout
                    sys.stdout = schema_buffer = io.StringIO()
                    try:
                        df.printSchema()
                        schema_str = schema_buffer.getvalue()
                        logger.log(log_level, f"[{name}] Schema:\n{schema_str}")
                    finally:
                        sys.stdout = old_stdout
                else:
                    logger.warning(f"[{name}] Unable to determine schema format")

            except Exception as e:
                logger.error(f"[{name}] Failed to display schema: {e}")

        # Show sample data if requested
        if show_sample:
            try:
                # Try to convert to Pandas for better display
                if hasattr(df, "limit") and hasattr(df, "toPandas"):
                    sample_data = df.limit(sample_rows).toPandas()
                    logger.log(
                        log_level, f"[{name}] Sample data ({sample_rows} rows):\n{sample_data}"
                    )
                elif hasattr(df, "show"):
                    # Alternative: use Spark's show method
                    import io
                    import sys

                    old_stdout = sys.stdout
                    sys.stdout = show_buffer = io.StringIO()
                    try:
                        df.show(sample_rows, truncate=False)
                        show_output = show_buffer.getvalue()
                        logger.log(
                            log_level, f"[{name}] Sample data ({sample_rows} rows):\n{show_output}"
                        )
                    finally:
                        sys.stdout = old_stdout
                else:
                    logger.warning(
                        f"[{name}] Unable to display sample data - unsupported DataFrame type"
                    )

            except Exception as e:
                logger.error(f"[{name}] Failed to display sample data: {e}")

        # Show statistics for numeric columns
        try:
            if hasattr(df, "dtypes") and hasattr(df, "select") and hasattr(df, "describe"):
                # Get numeric columns
                numeric_types = ["int", "bigint", "double", "float", "decimal", "long"]
                stats_cols = [
                    col_name
                    for col_name, col_type in df.dtypes
                    if any(num_type in col_type.lower() for num_type in numeric_types)
                ]

                if stats_cols:
                    stats_df = df.select(*stats_cols).describe()
                    if hasattr(stats_df, "toPandas"):
                        stats_data = stats_df.toPandas()
                        logger.log(
                            log_level, f"[{name}] Statistics for numeric columns:\n{stats_data}"
                        )
                    else:
                        logger.log(
                            log_level,
                            f"[{name}] Found {len(stats_cols)} numeric columns: {stats_cols}",
                        )
                else:
                    logger.log(log_level, f"[{name}] No numeric columns found for statistics")

        except Exception as e:
            logger.error(f"[{name}] Failed to compute statistics: {e}")

    except Exception as e:
        logger.error(f"[{name}] Unexpected error during DataFrame analysis: {e}")
        logger.debug(f"[{name}] DataFrame type: {type(df)}", exc_info=True)
