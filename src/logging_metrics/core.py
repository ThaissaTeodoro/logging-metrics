import os
import sys
import time
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from typing import List, Optional, Any

import pytz


def _make_timezone_converter(tz_name: str):
    """
    Creates a converter to apply timezone to epoch timestamps.

    Args:
        tz_name (str): Timezone name (e.g., 'America/Sao_Paulo').

    Returns:
        Function that converts a timestamp to a time.struct_time in the given timezone.
    """
    tz = pytz.timezone(tz_name)

    def converter(timestamp):
        # timestamp is a float (epoch)
        dt = datetime.fromtimestamp(timestamp, tz)
        return dt.timetuple()

    return converter


# ANSI Color Constants
class Colors:
    """ANSI colors for terminal formatting."""

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
    Custom formatter that adds color to terminal log output.

    Colors per level:
    - DEBUG: Cyan
    - INFO: Green
    - WARNING: Yellow
    - ERROR: Red
    - CRITICAL: Red background with white bold text
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
        self, fmt: str = None, datefmt: str = None, style: str = "%", use_colors: bool = True
    ):
        """
        Initializes the formatter with color support.

        Args:
            fmt: Format string for logs.
            datefmt: Date/time format string.
            style: Formatting style ('%', '{', or '$').
            use_colors: Whether to use ANSI colors (disable for unsupported environments).
        """
        if fmt is None:
            fmt = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
        if datefmt is None:
            datefmt = "%Y-%m-%d %H:%M:%S"

        super().__init__(fmt=fmt, datefmt=datefmt, style=style)
        self.use_colors = use_colors

    def format(self, record: logging.LogRecord) -> str:
        """
        Formats the log record with appropriate colors.

        Args:
            record: Log record to format.

        Returns:
            Colored formatted log message (if enabled).
        """
        # Save original attributes to restore after formatting
        original_levelname = record.levelname
        original_msg = record.msg

        # Add color if enabled
        if self.use_colors:
            # Colorize log level
            color = self.COLORS.get(record.levelno, Colors.RESET)
            record.levelname = f"{color}{record.levelname}{Colors.RESET}"

            # Colorize message for ERROR and CRITICAL
            if record.levelno >= logging.ERROR:
                record.msg = f"{color}{record.msg}{Colors.RESET}"

        # Format message
        formatted_message = super().format(record)

        # Restore original attributes
        record.levelname = original_levelname
        record.msg = original_msg

        return formatted_message


class JSONFormatter(logging.Formatter):
    """
    Formatter that outputs logs in JSON format for log analysis tools integration.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Formats a log record as JSON.

        Args:
            record: Log record to format.

        Returns:
            JSON string with log data.
        """
        import json

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

        # Add extra LogRecord data
        for key, value in record.__dict__.items():
            if key not in {
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
            }:
                log_data[key] = value

        return json.dumps(log_data)


def create_file_handler(
    log_file: str,
    max_bytes: int = 10485760,
    backup_count: int = 5,
    encoding: str = "utf-8",
    formatter: logging.Formatter = None,
    level: int = logging.DEBUG,
) -> logging.Handler:
    """
    Creates a file handler with size-based rotation.

    Args:
        log_file: Log file path.
        max_bytes: Maximum file size before rotation (default: 10MB).
        backup_count: Number of backup files to keep.
        encoding: Log file encoding.
        formatter: Custom formatter (optional).
        level: Minimum log level.

    Returns:
        Configured rotating file handler.
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(log_file)), exist_ok=True)

    # Create handler with rotation
    handler = RotatingFileHandler(
        log_file, maxBytes=max_bytes, backupCount=backup_count, encoding=encoding
    )

    handler.setLevel(level)

    if formatter is None:
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

    handler.setFormatter(formatter)
    return handler


def create_timed_file_handler(
    log_file: str,
    when: str = "midnight",
    interval: int = 1,
    backup_count: int = 7,
    encoding: str = "utf-8",
    formatter: logging.Formatter = None,
    level: int = logging.DEBUG,
) -> logging.Handler:
    """
    Creates a file handler with time-based rotation.

    Args:
        log_file: Log file path.
        when: When to rotate ('S', 'M', 'H', 'D', 'W0'-'W6', 'midnight').
        interval: Rotation interval.
        backup_count: Number of backup files to keep.
        encoding: Log file encoding.
        formatter: Custom formatter (optional).
        level: Minimum log level.

    Returns:
        Configured time-rotating file handler.
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(log_file)), exist_ok=True)

    # Create handler with time-based rotation
    handler = TimedRotatingFileHandler(
        log_file, when=when, interval=interval, backupCount=backup_count, encoding=encoding
    )

    handler.setLevel(level)

    if formatter is None:
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

    handler.setFormatter(formatter)
    return handler


def create_console_handler(
    level: int = logging.INFO, use_colors: bool = True, formatter: logging.Formatter = None
) -> logging.Handler:
    """
    Creates a console (stdout) handler with color support.

    Args:
        level: Minimum log level.
        use_colors: Whether to use color formatting.
        formatter: Custom formatter (optional).

    Returns:
        Configured console handler.
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    if formatter is None:
        formatter = ColoredFormatter(use_colors=use_colors)

    handler.setFormatter(formatter)
    return handler


def configure_basic_logging(
    level: int = logging.INFO,
    log_format: str = "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    date_format: str = "%Y-%m-%d %H:%M:%S",
    use_colors: bool = True,
) -> None:
    """
    Configures basic logging for console with color formatting.

    Args:
        level: Default log level.
        log_format: Log message format.
        date_format: Date/time format in logs.
        use_colors: Whether to use colors in the console.
    """
    # Remove existing handlers to avoid duplication
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    root_logger.setLevel(level)

    # Add console handler
    console_handler = create_console_handler(level=level, use_colors=use_colors)
    if use_colors:
        console_handler.setFormatter(
            ColoredFormatter(fmt=log_format, datefmt=date_format, use_colors=use_colors)
        )
    else:
        console_handler.setFormatter(logging.Formatter(fmt=log_format, datefmt=date_format))

    root_logger.addHandler(console_handler)

    return root_logger


def get_logger(
    name: str,
    level: Optional[int] = None,
    handlers: Optional[List[logging.Handler]] = None,
    propagate: Optional[bool] = None,
    caplog_friendly: bool = False,
) -> logging.Logger:
    """
    Creates or gets a logger with flexible configuration for production and pytest caplog.

    Args:
        name (str): Logger name.
        level (int, optional): Log level. If None, uses the default level.
        handlers (List[logging.Handler], optional): Handlers to add to the logger.
        propagate (bool, optional): If None, sets automatically according to caplog_friendly.
        caplog_friendly (bool): If True, does not add handlers and enables propagate.

    Returns:
        logging.Logger: Configured logger.
    """
    logger = logging.getLogger(name)

    # Set propagate automatically if not specified
    if propagate is None:
        propagate = caplog_friendly

    # Set level
    if level is not None:
        logger.setLevel(level)

    # caplog-friendly configuration
    if caplog_friendly:
        # Remove own handlers (so as not to "block" caplog)
        for h in logger.handlers[:]:
            logger.removeHandler(h)
        logger.propagate = True  # logs go to the root logger
    else:
        # Production: may have custom handlers and control propagate
        if handlers:
            for h in logger.handlers[:]:
                logger.removeHandler(h)
            for h in handlers:
                logger.addHandler(h)
        logger.propagate = propagate

    return logger


def setup_file_logging(
    logger_name: str,
    log_folder: str = "unknown/",
    log_dir: str = "./logs/",
    file_prefix: str = None,
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
    Configures a logger with file output (with rotation) and optional console output.

    Args:
        logger_name: Logger name.
        log_folder: Subfolder to save the logs.
        file_prefix: File prefix.
        level: File log level.
        console_level: Console log level.
        rotation: 'time' or 'size'.
        max_bytes: For size-based rotation.
        backup_count: Number of backup files.
        add_console: Add console handler.
        use_colors: Use colors in the console.
        log_format: Log format (when not using JSON).
        date_format: Date/time format.
        utc: Timezone to apply.
        json_format: If True, use JSONFormatter for file and console.
    """
    # Create directory
    log_dir = f"{log_dir}{log_folder}"
    os.makedirs(log_dir, exist_ok=True)

    # File name
    if file_prefix is None:
        file_prefix = logger_name.replace(".", "_")

    utc_tz = pytz.timezone(utc)
    timestamp = datetime.now(utc_tz).strftime("%Y%m%d_%H:%M:%S")

    extension = "json" if json_format else "log"
    log_file = os.path.join(log_dir, f"{timestamp}-{file_prefix}.{extension}")

    # Choose formatter
    if json_format:
        file_formatter = JSONFormatter()
    else:
        file_formatter = logging.Formatter(fmt=log_format, datefmt=date_format)
        file_formatter.converter = _make_timezone_converter(utc)

    handlers = []

    # File handler
    if rotation.lower() == "time":
        file_handler = create_timed_file_handler(
            log_file=log_file,
            level=level,
            formatter=file_formatter,
            backup_count=backup_count,
        )
    else:
        file_handler = create_file_handler(
            log_file=log_file,
            max_bytes=max_bytes,
            backup_count=backup_count,
            level=level,
            formatter=file_formatter,
        )
    handlers.append(file_handler)

    # Console handler
    if add_console:
        if json_format:
            console_formatter = JSONFormatter()
        else:
            console_formatter = ColoredFormatter(
                fmt=log_format, datefmt=date_format, use_colors=use_colors
            )
            console_formatter.converter = _make_timezone_converter(utc)

        console_handler = create_console_handler(
            level=console_level,
            use_colors=use_colors,
            formatter=console_formatter,
        )
        handlers.append(console_handler)

    # Create logger
    logger = get_logger(logger_name, level=level, handlers=handlers, propagate=False)

    logger.info(f"Logger configured: json_format={json_format}")

    # Method to close handlers
    def close():
        for handler in logger.handlers[:]:
            try:
                handler.flush()
                handler.close()
            except Exception as e:
                print(f"Error closing handler: {e}")
            logger.removeHandler(handler)

    logger.close = close

    return logger


class LogTimer:
    """
    Utility to measure and log execution time of operations.

    Can be used as a context manager:
    ```
    with LogTimer(logger, "Processing operation"):
        # code to be measured
    ```

    Or as a decorator:
    ```
    @LogTimer.as_decorator(logger, "Transformation function")
    def my_function():
        # code to be measured
    ```
    """

    def __init__(self, logger: logging.Logger, operation_name: str, level: int = logging.INFO):
        """
        Initializes the log timer.

        Args:
            logger: Logger for messages.
            operation_name: Name of the operation being timed.
            level: Log level for messages.
        """
        self.logger = logger
        self.operation_name = operation_name
        self.level = level
        self.start_time = None

    def __enter__(self):
        """Starts timing on entering the context."""
        self.start_time = time.time()
        self.logger.log(self.level, f"Starting: {self.operation_name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Logs time on exiting the context."""
        end_time = time.time()
        elapsed = end_time - self.start_time

        if exc_type is not None:
            # If there was an exception
            self.logger.error(
                f"Failure in '{self.operation_name}' after {elapsed:.2f} seconds. "
                f"Error: {exc_type.__name__}: {str(exc_val)}"
            )
        else:
            # Operation succeeded
            self.logger.log(
                self.level, f"Completed: {self.operation_name} in {elapsed:.2f} seconds."
            )

    @staticmethod
    def as_decorator(logger: logging.Logger, operation_name: str = None, level: int = logging.INFO):
        """
        Creates a decorator to measure function execution time.

        Args:
            logger: Logger for messages.
            operation_name: Name of the operation (if None, uses the function name).
            level: Log level for messages.

        Returns:
            Function decorator.
        """

        def decorator(func):
            import functools

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                op_name = operation_name if operation_name is not None else func.__name__
                with LogTimer(logger, op_name, level):
                    return func(*args, **kwargs)

            return wrapper

        return decorator


def log_spark_dataframe_info(
    df,
    logger: logging.Logger,
    name: str = "DataFrame",
    show_schema: bool = True,
    show_sample: bool = False,
    sample_rows: int = 5,
    log_level: int = logging.INFO,
):
    """
    Logs summary information about a PySpark DataFrame using the provided logger.

    Args:
        df (pyspark.sql.DataFrame): DataFrame to log.
        logger (logging.Logger): Logger to record the information.
        name (str): Reference name for the DataFrame (used in logs).
        show_schema (bool): If True, logs the DataFrame schema.
        show_sample (bool): If True, logs a data sample.
        sample_rows (int): Number of rows to display in the sample.
        log_level (int): Log level to use.

    Example:
        log_spark_dataframe_info(df, logger, name="BronzeLayer", show_schema=True)
    """
    if df is None:
        logger.warning(f"[{name}] DataFrame is None.")
        return

    try:
        row_count = df.count()
        logger.log(log_level, f"[{name}] Row count: {row_count}")
    except Exception as e:
        logger.error(f"[{name}] Error counting rows: {e}")

    if show_schema:
        try:
            schema_str = df._jdf.schema().treeString()
            logger.log(log_level, f"[{name}] Schema:\n{schema_str}")
        except Exception as e:
            logger.error(f"[{name}] Error displaying schema: {e}")

    if show_sample:
        try:
            sample_data = df.limit(sample_rows).toPandas()
            logger.log(log_level, f"[{name}] Sample ({sample_rows} rows):\n{sample_data}")
        except Exception as e:
            logger.error(f"[{name}] Error displaying sample: {e}")

    try:
        stats_cols = [
            c for c, t in df.dtypes if t in ["int", "bigint", "double", "float", "decimal", "long"]
        ]
        if stats_cols:
            stats = df.select(*stats_cols).describe().toPandas()
            logger.log(log_level, f"[{name}] Statistics:\n{stats}")
    except Exception as e:
        logger.error(f"[{name}] Error computing statistics: {e}")


class LogMetrics:
    """
    Utility class to collect and log processing metrics.

    Example:
    ```
    metrics = LogMetrics(logger)
    metrics.start('total_processing')

    metrics.increment('records_processed')
    metrics.increment('records_processed')
    metrics.increment('errors', 1)

    metrics.set('batch_size', 1000)

    metrics.stop('total_processing')
    metrics.log_all()
    ```
    """

    def __init__(self, logger: logging.Logger, level: int = logging.INFO):
        """
        Initializes the metrics collector.

        Args:
            logger: Logger to record metrics.
            level: Log level for metrics.
        """
        self.logger = logger
        self.level = level
        self.counters = {}
        self.values = {}
        self.timers = {}

    def increment(self, metric_name: str, value: int = 1):
        """
        Increments a metric counter.

        Args:
            metric_name: Metric name.
            value: Increment value (default: 1).
        """
        if metric_name not in self.counters:
            self.counters[metric_name] = 0
        self.counters[metric_name] += value

    def set(self, metric_name: str, value: Any):
        """
        Sets a value for a metric.

        Args:
            metric_name: Metric name.
            value: Value to set.
        """
        self.values[metric_name] = value

    def start(self, timer_name: str):
        """
        Starts a timer to measure operation time.

        Args:
            timer_name: Timer name.
        """
        self.timers[timer_name] = {"start": time.time(), "elapsed": None}

    def stop(self, timer_name: str) -> float:
        """
        Stops a timer and calculates elapsed time.

        Args:
            timer_name: Timer name.

        Returns:
            Elapsed time in seconds.
        """
        if timer_name in self.timers and "start" in self.timers[timer_name]:
            elapsed = time.time() - self.timers[timer_name]["start"]
            self.timers[timer_name]["elapsed"] = elapsed
            return elapsed
        return 0.0

    def log(self, metric_name: str, value: Any = None):
        """
        Logs a specific metric.

        Args:
            metric_name: Metric name.
            value: Optional value to override.
        """
        if value is not None:
            self.logger.log(self.level, f"Metric '{metric_name}': {value}")
            return

        if metric_name in self.counters:
            self.logger.log(self.level, f"Counter '{metric_name}': {self.counters[metric_name]}")
        elif metric_name in self.values:
            self.logger.log(self.level, f"Value '{metric_name}': {self.values[metric_name]}")
        elif metric_name in self.timers and self.timers[metric_name].get("elapsed") is not None:
            elapsed = self.timers[metric_name]["elapsed"]
            self.logger.log(self.level, f"Timer '{metric_name}': {elapsed:.2f} seconds")

    def log_all(self):
        """
        Logs all collected metrics.
        """
        self.logger.log(self.level, "--- Processing Metrics ---")

        # Log counters
        if self.counters:
            self.logger.log(self.level, "Counters:")
            for name, value in self.counters.items():
                self.logger.log(self.level, f"  - {name}: {value}")

        # Log values
        if self.values:
            self.logger.log(self.level, "Values:")
            for name, value in self.values.items():
                self.logger.log(self.level, f"  - {name}: {value}")

        # Log timers
        active_timers = []
        completed_timers = []

        for name, timer in self.timers.items():
            if timer.get("elapsed") is not None:
                completed_timers.append((name, timer["elapsed"]))
            else:
                # Timer still active
                current = time.time() - timer["start"]
                active_timers.append((name, current))

        if completed_timers:
            self.logger.log(self.level, "Completed timers:")
            for name, elapsed in completed_timers:
                self.logger.log(self.level, f"  - {name}: {elapsed:.2f} seconds")

        if active_timers:
            self.logger.log(self.level, "Active timers:")
            for name, current in active_timers:
                self.logger.log(self.level, f"  - {name}: {current:.2f} seconds (running)")

        self.logger.log(self.level, "--------------------------------")
