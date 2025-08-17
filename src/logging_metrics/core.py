"""
Backward compatibility module for logging-metrics.

This module maintains 100% backward compatibility with previous versions by
importing and re-exporting all functionality from the new modular structure.
Existing code using 'from logging_metrics.core import ...' will continue
to work without any changes.

Note:
    For new projects, consider using the modular imports:
    - from logging_metrics.logger import setup_file_logging
    - from logging_metrics.timers import LogTimer
    - from logging_metrics.metrics import LogMetrics
"""

# Import all functionality from the new modular structure for backward compatibility
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

# Re-export everything for backward compatibility
__all__ = [
    # Logger functionality
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
    # Timer functionality
    "LogTimer",
    # Metrics functionality
    "LogMetrics",
    "TimerContext",
]
