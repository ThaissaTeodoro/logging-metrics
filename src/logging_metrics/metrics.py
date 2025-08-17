"""
Metrics collection and logging utilities.

This module provides comprehensive metrics collection capabilities including counters,
values, and timers. The LogMetrics class is designed for monitoring application
performance and behavior with automatic logging and programmatic access.
"""

import logging
import time
from typing import Any, Dict, List, Optional, Tuple

# Public API definition
__all__ = ["LogMetrics", "TimerContext"]


class TimerContext:
    """
    Context manager for timing operations within LogMetrics.

    This class provides a context manager interface for timing operations
    and automatically recording the results in a LogMetrics instance.

    Args:
        metrics: LogMetrics instance to record timing results.
        timer_name: Name for the timer operation.

    Raises:
        TypeError: If metrics is not a LogMetrics instance.
        ValueError: If timer_name is empty.

    Example:
        >>> metrics = LogMetrics(logger)
        >>> with TimerContext(metrics, 'database_operation'):
        ...     result = database.query("SELECT * FROM users")
    """

    def __init__(self, metrics: "LogMetrics", timer_name: str) -> None:
        """
        Initialize the timer context.

        Args:
            metrics: LogMetrics instance for recording results.
            timer_name: Name for the timer operation.

        Raises:
            TypeError: If metrics is not a LogMetrics instance.
            ValueError: If timer_name is empty.
        """
        if not isinstance(metrics, LogMetrics):
            raise TypeError("metrics must be a LogMetrics instance")

        if not isinstance(timer_name, str) or not timer_name.strip():
            raise ValueError("timer_name must be a non-empty string")

        self.metrics = metrics
        self.timer_name = timer_name.strip()

    def __enter__(self) -> "TimerContext":
        """
        Start the timer when entering context.

        Returns:
            Self for method chaining.
        """
        self.metrics.start(self.timer_name)
        return self

    def __exit__(
        self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Optional[Any]
    ) -> None:
        """
        Stop the timer when exiting context.

        Args:
            exc_type: Exception type if an exception occurred, None otherwise.
            exc_val: Exception instance if an exception occurred, None otherwise.
            exc_tb: Exception traceback if an exception occurred, None otherwise.
        """
        self.metrics.stop(self.timer_name)


class LogMetrics:
    """
    Comprehensive metrics collection and logging utility.

    This class provides a centralized way to collect, manage, and log various types
    of metrics including counters, values, and timers. It's designed for monitoring
    application performance, tracking business metrics, and debugging.

    Args:
        logger: Logger instance for outputting metrics.
        level: Default log level for metrics output.

    Raises:
        TypeError: If logger is not a Logger instance.
        ValueError: If level is invalid.

    Example:
        >>> metrics = LogMetrics(logger)
        >>> metrics.increment('requests_processed')
        >>> metrics.set('current_users', 150)
        >>> with metrics.timer('response_time'):
        ...     process_request()
        >>> metrics.log_all()
    """

    def __init__(self, logger: logging.Logger, level: int = logging.INFO) -> None:
        """
        Initialize the metrics collector.

        Args:
            logger: Logger instance for metrics output.
            level: Default log level for metrics messages.

        Raises:
            TypeError: If logger is not a Logger instance.
            ValueError: If level is invalid.
        """
        if not isinstance(logger, logging.Logger):
            raise TypeError("logger must be a logging.Logger instance")

        if not isinstance(level, int) or level < 0:
            raise ValueError(f"level must be a non-negative integer, got {level}")

        self.logger = logger
        self.level = level
        self.counters: Dict[str, int] = {}
        self.values: Dict[str, Any] = {}
        self.timers: Dict[str, Dict[str, Optional[float]]] = {}

    def increment(self, metric_name: str, value: int = 1) -> None:
        """
        Increment a counter metric.

        Args:
            metric_name: Name of the counter metric.
            value: Amount to increment (can be negative for decrement).

        Raises:
            ValueError: If metric_name is empty.
            TypeError: If value is not an integer.

        Example:
            >>> metrics.increment('page_views')
            >>> metrics.increment('errors', 3)
            >>> metrics.increment('cache_hits', -1)  # Decrement
        """
        if not isinstance(metric_name, str) or not metric_name.strip():
            raise ValueError("metric_name must be a non-empty string")

        if not isinstance(value, int):
            raise TypeError(f"value must be an integer, got {type(value).__name__}")

        metric_name = metric_name.strip()

        if metric_name not in self.counters:
            self.counters[metric_name] = 0

        self.counters[metric_name] += value

    def set(self, metric_name: str, value: Any) -> None:
        """
        Set a value metric.

        Value metrics can store any type of data and represent the current state
        of a particular measurement.

        Args:
            metric_name: Name of the value metric.
            value: Value to store (any type).

        Raises:
            ValueError: If metric_name is empty.

        Example:
            >>> metrics.set('current_temperature', 23.5)
            >>> metrics.set('active_users', 1250)
            >>> metrics.set('last_update', datetime.now())
            >>> metrics.set('status', 'healthy')
        """
        if not isinstance(metric_name, str) or not metric_name.strip():
            raise ValueError("metric_name must be a non-empty string")

        self.values[metric_name.strip()] = value

    def start(self, timer_name: str) -> None:
        """
        Start a timer metric.

        Args:
            timer_name: Name of the timer.

        Raises:
            ValueError: If timer_name is empty.
            RuntimeError: If timer is already running.

        Example:
            >>> metrics.start('api_call')
            >>> # ... perform operation ...
            >>> elapsed = metrics.stop('api_call')
        """
        if not isinstance(timer_name, str) or not timer_name.strip():
            raise ValueError("timer_name must be a non-empty string")

        timer_name = timer_name.strip()

        if timer_name in self.timers and self.timers[timer_name].get("elapsed") is None:
            raise RuntimeError(f"Timer '{timer_name}' is already running")

        self.timers[timer_name] = {"start": time.perf_counter(), "elapsed": None}

    def stop(self, timer_name: str) -> float:
        """
        Stop a timer metric and calculate elapsed time.

        Args:
            timer_name: Name of the timer to stop.

        Returns:
            Elapsed time in seconds.

        Raises:
            ValueError: If timer_name is empty.
            RuntimeError: If timer was not started or already stopped.

        Example:
            >>> metrics.start('database_query')
            >>> # ... execute query ...
            >>> elapsed = metrics.stop('database_query')
            >>> print(f"Query took {elapsed:.3f} seconds")
        """
        if not isinstance(timer_name, str) or not timer_name.strip():
            raise ValueError("timer_name must be a non-empty string")

        timer_name = timer_name.strip()

        if timer_name not in self.timers:
            raise RuntimeError(f"Timer '{timer_name}' was not started")

        timer_data = self.timers[timer_name]
        if timer_data.get("elapsed") is not None:
            raise RuntimeError(f"Timer '{timer_name}' was already stopped")

        if timer_data.get("start") is None:
            raise RuntimeError(f"Timer '{timer_name}' has invalid state")

        elapsed = time.perf_counter() - timer_data["start"]
        timer_data["elapsed"] = elapsed

        return elapsed

    def timer(self, timer_name: str) -> TimerContext:
        """
        Get a context manager for timing operations.

        Args:
            timer_name: Name for the timer operation.

        Returns:
            TimerContext instance for use in 'with' statements.

        Raises:
            ValueError: If timer_name is empty.

        Example:
            >>> with metrics.timer('file_processing'):
            ...     process_large_file()
            >>>
            >>> # Timer is automatically started and stopped
        """
        return TimerContext(self, timer_name)

    def log(self, metric_name: str, value: Optional[Any] = None) -> None:
        """
        Log a specific metric.

        Args:
            metric_name: Name of the metric to log.
            value: Optional value to override the stored metric value.

        Raises:
            ValueError: If metric_name is empty or metric doesn't exist.

        Example:
            >>> metrics.log('requests_processed')
            >>> metrics.log('custom_metric', 'special_value')
        """
        if not isinstance(metric_name, str) or not metric_name.strip():
            raise ValueError("metric_name must be a non-empty string")

        metric_name = metric_name.strip()

        # Use provided value if given
        if value is not None:
            self.logger.log(self.level, f"Metric '{metric_name}': {value}")
            return

        # Look for the metric in different collections
        if metric_name in self.counters:
            self.logger.log(self.level, f"Counter '{metric_name}': {self.counters[metric_name]}")
        elif metric_name in self.values:
            self.logger.log(self.level, f"Value '{metric_name}': {self.values[metric_name]}")
        elif metric_name in self.timers:
            timer_data = self.timers[metric_name]
            if timer_data.get("elapsed") is not None:
                elapsed = timer_data["elapsed"]
                self.logger.log(self.level, f"Timer '{metric_name}': {elapsed:.3f} seconds")
            else:
                current_elapsed = time.perf_counter() - timer_data["start"]
                self.logger.log(
                    self.level, f"Timer '{metric_name}': {current_elapsed:.3f} seconds (running)"
                )
        else:
            raise ValueError(f"Metric '{metric_name}' not found")

    def log_all(self) -> None:
        """
        Log all collected metrics in an organized format.

        This method outputs a comprehensive summary of all metrics including
        counters, values, and timers (both completed and active).

        Example:
            >>> metrics.log_all()
            # Output:
            # --- Processing Metrics ---
            # Counters:
            #   - requests: 150
            #   - errors: 3
            # Values:
            #   - status: healthy
            #   - uptime: 3600
            # Completed timers:
            #   - startup: 2.450 seconds
            # --------------------------------
        """
        self.logger.log(self.level, "--- Processing Metrics ---")

        # Log counters
        if self.counters:
            self.logger.log(self.level, "Counters:")
            for name, value in sorted(self.counters.items()):
                self.logger.log(self.level, f"  - {name}: {value}")

        # Log values
        if self.values:
            self.logger.log(self.level, "Values:")
            for name, value in sorted(self.values.items()):
                self.logger.log(self.level, f"  - {name}: {value}")

        # Categorize timers
        active_timers: List[Tuple[str, float]] = []
        completed_timers: List[Tuple[str, float]] = []

        for name, timer_data in self.timers.items():
            if timer_data.get("elapsed") is not None:
                completed_timers.append((name, timer_data["elapsed"]))
            else:
                # Timer still active
                current_elapsed = time.perf_counter() - timer_data["start"]
                active_timers.append((name, current_elapsed))

        # Log completed timers
        if completed_timers:
            self.logger.log(self.level, "Completed timers:")
            for name, elapsed in sorted(completed_timers):
                self.logger.log(self.level, f"  - {name}: {elapsed:.3f} seconds")

        # Log active timers
        if active_timers:
            self.logger.log(self.level, "Active timers:")
            for name, current_elapsed in sorted(active_timers):
                self.logger.log(self.level, f"  - {name}: {current_elapsed:.3f} seconds (running)")

        # Add separator
        self.logger.log(self.level, "--------------------------------")

    def reset(self) -> None:
        """
        Reset all metrics, counters, values, and timers.

        This method clears all collected data, allowing the metrics instance
        to be reused for a fresh collection cycle.

        Warning:
            This operation is irreversible. All collected metrics data will be lost.

        Example:
            >>> metrics.increment('requests', 100)
            >>> metrics.set('status', 'active')
            >>> metrics.reset()
            >>> # All metrics are now cleared
        """
        self.counters.clear()
        self.values.clear()
        self.timers.clear()

    def get_summary(self) -> Dict[str, Any]:
        """
        Get a programmatic summary of all current metrics.

        Returns:
            Dictionary containing all metrics data organized by type.
            Structure:
            {
                'counters': dict,
                'values': dict,
                'completed_timers': dict,
                'active_timers': dict
            }

        Example:
            >>> summary = metrics.get_summary()
            >>> print(f"Total requests: {summary['counters'].get('requests', 0)}")
            >>> print(f"Active timers: {list(summary['active_timers'].keys())}")
        """
        active_timers: Dict[str, float] = {}
        completed_timers: Dict[str, float] = {}

        for name, timer_data in self.timers.items():
            if timer_data.get("elapsed") is not None:
                completed_timers[name] = timer_data["elapsed"]
            else:
                current_elapsed = time.perf_counter() - timer_data["start"]
                active_timers[name] = current_elapsed

        return {
            "counters": self.counters.copy(),
            "values": self.values.copy(),
            "completed_timers": completed_timers,
            "active_timers": active_timers,
        }

    def get_counter(self, metric_name: str) -> int:
        """
        Get the current value of a counter metric.

        Args:
            metric_name: Name of the counter metric.

        Returns:
            Current counter value, or 0 if counter doesn't exist.

        Example:
            >>> count = metrics.get_counter('requests_processed')
            >>> print(f"Processed {count} requests")
        """
        return self.counters.get(metric_name.strip(), 0)

    def get_value(self, metric_name: str, default: Any = None) -> Any:
        """
        Get the current value of a value metric.

        Args:
            metric_name: Name of the value metric.
            default: Default value to return if metric doesn't exist.

        Returns:
            Current metric value, or default if metric doesn't exist.

        Example:
            >>> status = metrics.get_value('application_status', 'unknown')
            >>> print(f"Application status: {status}")
        """
        return self.values.get(metric_name.strip(), default)

    def get_timer_elapsed(self, timer_name: str) -> Optional[float]:
        """
        Get elapsed time for a timer (completed or running).

        Args:
            timer_name: Name of the timer.

        Returns:
            Elapsed time in seconds, or None if timer doesn't exist.

        Example:
            >>> elapsed = metrics.get_timer_elapsed('api_call')
            >>> if elapsed is not None:
            ...     print(f"API call took {elapsed:.3f} seconds")
        """
        timer_name = timer_name.strip()

        if timer_name not in self.timers:
            return None

        timer_data = self.timers[timer_name]

        if timer_data.get("elapsed") is not None:
            # Timer is completed
            return timer_data["elapsed"]
        else:
            # Timer is still running
            return time.perf_counter() - timer_data["start"]

    def has_metric(self, metric_name: str) -> bool:
        """
        Check if a metric exists in any collection.

        Args:
            metric_name: Name of the metric to check.

        Returns:
            True if metric exists, False otherwise.

        Example:
            >>> if metrics.has_metric('requests_processed'):
            ...     print("Request counter is active")
        """
        metric_name = metric_name.strip()
        return (
            metric_name in self.counters or metric_name in self.values or metric_name in self.timers
        )

    def list_metrics(self) -> Dict[str, List[str]]:
        """
        Get a list of all metric names organized by type.

        Returns:
            Dictionary with metric names grouped by type:
            {'counters': [...], 'values': [...], 'timers': [...]}

        Example:
            >>> metric_names = metrics.list_metrics()
            >>> print(f"Available counters: {metric_names['counters']}")
        """
        return {
            "counters": list(self.counters.keys()),
            "values": list(self.values.keys()),
            "timers": list(self.timers.keys()),
        }

    def __repr__(self) -> str:
        """
        Return string representation of the LogMetrics instance.

        Returns:
            String representation including counts of each metric type.
        """
        active_timers = sum(1 for timer in self.timers.values() if timer.get("elapsed") is None)
        completed_timers = len(self.timers) - active_timers

        return (
            f"LogMetrics("
            f"counters={len(self.counters)}, "
            f"values={len(self.values)}, "
            f"timers={len(self.timers)} "
            f"[{completed_timers} completed, {active_timers} active]"
            f")"
        )
