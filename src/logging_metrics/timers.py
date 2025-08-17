"""
Timing utilities for measuring and logging execution time.

This module provides the LogTimer class for measuring execution time of operations
with comprehensive logging support. It can be used both as a context manager and
as a decorator for flexible timing measurements.
"""

import functools
import logging
import time
from typing import Any, Callable, Optional

# Public API definition
__all__ = ["LogTimer"]


class LogTimer:
    """
    Utility for measuring and logging execution time of operations.

    This class provides flexible timing capabilities with automatic logging of
    start, completion, and failure events. It supports both context manager
    and decorator usage patterns.

    Args:
        logger: Logger instance to use for timing messages.
        operation_name: Descriptive name for the operation being timed.
        level: Log level for informational messages (start/completion).

    Raises:
        TypeError: If logger is not a Logger instance.
        ValueError: If operation_name is empty or level is invalid.

    Example:
        As a context manager:
        >>> with LogTimer(logger, "Database query"):
        ...     result = database.execute("SELECT * FROM users")

        As a decorator:
        >>> @LogTimer.as_decorator(logger, "Data processing")
        ... def process_data(data):
        ...     return transform(data)
    """

    def __init__(
        self, logger: logging.Logger, operation_name: str, level: int = logging.INFO
    ) -> None:
        """
        Initialize the LogTimer.

        Args:
            logger: Logger instance for timing messages.
            operation_name: Name of the operation being timed.
            level: Log level for start/completion messages.

        Raises:
            TypeError: If logger is not a Logger instance.
            ValueError: If operation_name is empty or level is invalid.
        """
        if not isinstance(logger, logging.Logger):
            raise TypeError("logger must be a logging.Logger instance")

        if not isinstance(operation_name, str) or not operation_name.strip():
            raise ValueError("operation_name must be a non-empty string")

        if not isinstance(level, int) or level < 0:
            raise ValueError(f"level must be a non-negative integer, got {level}")

        self.logger = logger
        self.operation_name = operation_name.strip()
        self.level = level
        self.start_time: Optional[float] = None

    def __enter__(self) -> "LogTimer":
        """
        Start timing when entering the context.

        Returns:
            Self for method chaining.
        """
        self.start_time = time.perf_counter()
        self.logger.log(self.level, f"Starting: {self.operation_name}")
        return self

    def __exit__(
        self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Optional[Any]
    ) -> None:
        """
        Log timing results when exiting the context.

        Args:
            exc_type: Exception type if an exception occurred, None otherwise.
            exc_val: Exception instance if an exception occurred, None otherwise.
            exc_tb: Exception traceback if an exception occurred, None otherwise.
        """
        if self.start_time is None:
            self.logger.error(f"Timer for '{self.operation_name}' was not properly started")
            return

        try:
            end_time = time.perf_counter()
            elapsed = end_time - self.start_time

            if exc_type is not None:
                # Operation failed with an exception
                self.logger.error(
                    f"Failed: '{self.operation_name}' after {elapsed:.3f} seconds. "
                    f"Error: {exc_type.__name__}: {exc_val}"
                )
            else:
                # Operation completed successfully
                self.logger.log(
                    self.level, f"Completed: {self.operation_name} in {elapsed:.3f} seconds"
                )

        except Exception as e:
            # Error during timing calculation (should be very rare)
            self.logger.error(f"Error calculating timing for '{self.operation_name}': {e}")

    def start(self) -> None:
        """
        Manually start the timer.

        This method allows manual control of timing, useful when context manager
        usage is not suitable.

        Raises:
            RuntimeError: If timer is already running.
        """
        if self.start_time is not None:
            raise RuntimeError(f"Timer for '{self.operation_name}' is already running")

        self.start_time = time.perf_counter()
        self.logger.log(self.level, f"Starting: {self.operation_name}")

    def stop(self) -> float:
        """
        Manually stop the timer and log results.

        Returns:
            Elapsed time in seconds.

        Raises:
            RuntimeError: If timer was not started.
        """
        if self.start_time is None:
            raise RuntimeError(f"Timer for '{self.operation_name}' was not started")

        try:
            end_time = time.perf_counter()
            elapsed = end_time - self.start_time
            self.start_time = None  # Reset for potential reuse

            self.logger.log(
                self.level, f"Completed: {self.operation_name} in {elapsed:.3f} seconds"
            )

            return elapsed

        except Exception as e:
            self.logger.error(f"Error stopping timer for '{self.operation_name}': {e}")
            self.start_time = None  # Reset even on error
            return 0.0

    def elapsed(self) -> float:
        """
        Get current elapsed time without stopping the timer.

        Returns:
            Current elapsed time in seconds, or 0.0 if timer not started.
        """
        if self.start_time is None:
            return 0.0

        return time.perf_counter() - self.start_time

    @staticmethod
    def as_decorator(
        logger: logging.Logger, operation_name: Optional[str] = None, level: int = logging.INFO
    ) -> Callable[[Callable], Callable]:
        """
        Create a decorator for timing function execution.

        Args:
            logger: Logger instance for timing messages.
            operation_name: Name for the operation. If None, uses function name.
            level: Log level for timing messages.

        Returns:
            Decorator function that wraps the target function with timing.

        Raises:
            TypeError: If logger is not a Logger instance.
            ValueError: If level is invalid.

        Example:
            >>> @LogTimer.as_decorator(logger, "Data transformation")
            ... def transform_data(data):
            ...     return process(data)

            >>> @LogTimer.as_decorator(logger)  # Uses function name
            ... def calculate_metrics():
            ...     return compute()
        """
        if not isinstance(logger, logging.Logger):
            raise TypeError("logger must be a logging.Logger instance")

        if not isinstance(level, int) or level < 0:
            raise ValueError(f"level must be a non-negative integer, got {level}")

        def decorator(func: Callable) -> Callable:
            """
            Decorator that wraps a function with timing measurement.

            Args:
                func: Function to be timed.

            Returns:
                Wrapped function with timing capabilities.
            """
            # Determine operation name
            op_name = operation_name if operation_name is not None else func.__name__

            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                """
                Wrapper function that times the execution of the target function.

                Args:
                    *args: Positional arguments to pass to the target function.
                    **kwargs: Keyword arguments to pass to the target function.

                Returns:
                    The return value of the target function.
                """
                with LogTimer(logger, op_name, level):
                    return func(*args, **kwargs)

            return wrapper

        return decorator

    def __repr__(self) -> str:
        """
        Return string representation of the LogTimer.

        Returns:
            String representation including operation name and current state.
        """
        status = "running" if self.start_time is not None else "stopped"
        elapsed_info = f", elapsed={self.elapsed():.3f}s" if self.start_time is not None else ""
        return f"LogTimer(operation='{self.operation_name}', status={status}{elapsed_info})"
