"""
Advanced logging utilities for robust, standardized logs in Python projects.

This package provides comprehensive logging functionality including colored formatters,
file rotation, metrics collection, timing utilities, and PySpark integration.
All components are designed for production use with robust error handling.

Example:
    Basic usage:
    >>> from logging_metrics import setup_file_logging, LogTimer, LogMetrics
    >>> logger = setup_file_logging("myapp", log_dir="./logs")
    >>>
    >>> with LogTimer(logger, "Startup process"):
    ...     initialize_application()
    >>>
    >>> metrics = LogMetrics(logger)
    >>> metrics.increment('users_processed', 150)
    >>> metrics.log_all()

    Modular usage:
    >>> from logging_metrics.logger import configure_basic_logging
    >>> from logging_metrics.timers import LogTimer
    >>> from logging_metrics.metrics import LogMetrics
    >>>
    >>> logger = configure_basic_logging()
    >>> # ... rest of the code
"""

# Version information
__version__ = "1.0.0"
__version_info__ = (1, 0, 0)

# Import from modular structure
from .logger import (
    ColoredFormatter,
    Colors,
    JSONFormatter,
    configure_basic_logging,
    create_console_handler,
    create_file_handler,
    create_timed_file_handler,
    get_logger,
    log_spark_dataframe_info,
    setup_file_logging,
)
from .metrics import LogMetrics, TimerContext
from .timers import LogTimer

# Public API definition
__all__ = [
    # Version info
    "__version__",
    "__version_info__",
    # Logger module
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
    # Timers module
    "LogTimer",
    # Metrics module
    "LogMetrics",
    "TimerContext",
]


def get_version() -> str:
    """
    Get the current version string.

    Returns:
        Version string in format "MAJOR.MINOR.PATCH".

    Example:
        >>> from logging_metrics import get_version
        >>> print(f"Using logging-metrics version: {get_version()}")
    """
    return __version__


def get_version_info() -> tuple:
    """
    Get the current version as a tuple.

    Returns:
        Version tuple (major, minor, patch).

    Example:
        >>> from logging_metrics import get_version_info
        >>> major, minor, patch = get_version_info()
        >>> print(f"Version: {major}.{minor}.{patch}")
    """
    return __version_info__
