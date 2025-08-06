
# logging-metrics - Utilities Library for Logging Configuration and Management

This module provides functions and classes to configure logging for different environments and use cases:

- Colored logs for the terminal
- Rotating log files (by time or size)
- Customizable settings for different verbosity levels
- Text or JSON formatters compatible with external analysis tools
- Utilities for timing operations and collecting custom metrics
- **Utility functions for logging PySpark DataFrames** (e.g., row count, schema, samples, and basic statistics)

Main Components:
----------------
- `ColoredFormatter`: Colorized terminal output for quick identification of log levels
- `JSONFormatter`: JSON-formatted logs for external tool integration
- Functions to create handlers (console, file, rotation by time or size)
- `LogTimer`: Measure execution time of code blocks (context manager or decorator)
- `LogMetrics`: Collect and log custom metrics (counters, timers, values)
- `log_spark_dataframe_info`: Easy, structured logging for PySpark DataFrames

This toolkit is recommended for data pipelines, ETLs, and projects where traceability, auditability, and log performance are critical requirements.

---

This README.md covers:

- Purpose
- Installation
- Main Features
- Best Practices
- Usage Example
- Spark Integration
- Dependencies & License

---

# logging-metrics

A library for configuring and managing logs in Python, focused on simplicity and performance.

---

#### ✨ Features

- 🎨 Colored logs for the terminal with different levels
- 📁 Automatic file rotation by time or size
- ⚡ PySpark DataFrame integration
- 📊 JSON format for observability systems
- ⏱️ Timing with LogTimer
- 📈 Metrics monitoring with LogMetrics
- 🔧 Hierarchical logger configuration
- 🚀 Optimized performance for critical applications

---

## 📦 Installation

#### Install via pip:
```bash
pip install logging-metrics 
```

#### For development:
```bash
git clone https://github.com/thaissateodoro/logging-metrics.git
cd logging-metrics
pip install -e ".[dev]"
```

---
## 📋 Functions and Classes Overview

Main Functions
```
| Name                      | Type     | Description                                                                          |
|---------------------------|----------|--------------------------------------------------------------------------------------|
| `configure_basic_logging` | Function | Configures root logger for colored console logging.                                  |
| `setup_file_logging`      | Function | Configures a logger with file output (rotation), optional console, JSON formatting.  |
| `LogTimer`                | Class    | Context manager and decorator to log execution time of code blocks or functions.     |
| `log_spark_dataframe_info`| Function | Logs schema, sample, stats of a PySpark DataFrame (row count, sample, stats, etc).   |
| `LogMetrics`              | Class    | Utility for collecting, incrementing, timing, and logging custom processing metrics. |
| `get_logger`              | Function | Returns a logger with custom handlers and caplog-friendly mode for pytest.           |
```
---

### Utility Classes
#### LogTimer
- Context manager: with LogTimer(logger, "operation"):
- Decorator: @LogTimer.decorator(logger, "function")
- Manual: timer.start() / timer.stop()

#### LogMetrics
- Counters: metrics.increment('counter')
- Timers: metrics.start('timer') / metrics.stop('timer')
- Context manager: with metrics.timer('operation'):
- Report: metrics.log_all()

---

## 🚀 Quick Start

```python
import logging
from logging_metrics import setup_file_logging, LogTimer

# Basic configuration
logger = setup_file_logging(
    logger_name="my_app",
    log_dir="./logs",
    console_level=logging.INFO,  # Less verbose in console
    level=logging.DEBUG          # More detailed in the file
)

# Simple usage
logger.info("Application started!")

# Timing operations
with LogTimer(logger, "Critical operation"):
    # your code here
    pass
```

---

## 📖 Main Features

1. Logging configuration:
    ```python
    import logging
    from logging-metrics import configure_basic_logging
    logger = configure_basic_logging()
    logger.debug("Debug message")     # Gray
    logger.info("Info")               # Green  
    logger.warning("Warning")         # Yellow
    logger.error("Error")             # Red
    logger.critical("Critical")       # Bold red
    ```

2. Automatic Log Rotation:
    ```python
    from logging-metrics import setup_file_logging, LogTimer
    # Size-based rotation
    logger = setup_file_logging(
        logger_name="app",
        log_dir="./logs",
        max_bytes=10*1024*1024,  # 10MB
        rotation='size'
    )
    
    # Time-based rotation
    logger = setup_file_logging(
        logger_name="app", 
        log_dir="./logs",
        rotation='time'    
    )
    ```

3. Spark/Databricks Integration:
    ```python
    from pyspark.sql import SparkSession
    from logging_metrics import configure_basic_logging, log_spark_dataframe_info
    
    spark = SparkSession.builder.getOrCreate()
    df = spark.createDataFrame([(1, "Ana"), (2, "Bruno")], ["id", "nome"])
    
    logger = configure_basic_logging()
    print("Logger:", logger)
    
    log_spark_dataframe_info(
        df = df,logger = logger, name ="spark_app")
    
    logger.info("Spark processing started")
    ```

4. ⏱ Timing with LogTimer:
    ```python
    from logging_metrics import LogTimer, configure_basic_logging

    logger = configure_basic_logging()
    # As a context manager
    with LogTimer(logger, "DB query"):
        logger.info("Test")
    
    # As a decorator
    @LogTimer.as_decorator(logger, "Data processing")
    def process_data(data):
        return data.transform()
        ```

5. 📈 Metrics Monitoring:
    ```python
   from logging_metrics import LogMetrics, configure_basic_logging
    import time
    
    logger = configure_basic_logging()
    
    metrics = LogMetrics(logger)
    
    items = [10, 5, 80, 60, 'test1', 'test2']
    
    # Start timer for total operation
    metrics.start('total_processing')
    
    
    for item in items:
        # Increments the processed records counter
        metrics.increment('records_processed')

        # If it is an error (simulation)
        if isinstance(item, str):
            metrics.increment('errors')
    
        # Simulates item processing
        time.sleep(0.1)
    
        # Custom value example
        metrics.set('last_item', item)
    
    
    # Finalize and log all metrics
    elapsed = metrics.stop('total_processing')
    
    # Logs all collected metrics
    metrics.log_all()
    
    # Output:
    # --- Processing Metrics ---
    # Counters:
    #   - records_processed: 6
    #   - errors_found: 2
    #  Values:
    #   - last_item: test2
    #  Completed timers:
    #   - total_processing: 0.60 seconds
    ```

6. Hierarchical Configuration:
    ```python
   from logging_metrics import setup_file_logging
    import logging
    
    # Main logger
    main_logger = setup_file_logging("my_app", log_dir="./logs")
    
    # Sub-loggers organized hierarchically
    db_logger = logging.getLogger("my_app.database")
    api_logger = logging.getLogger("my_app.api")
    auth_logger = logging.getLogger("my_app.auth")
    
    # Module-specific configuration
    db_logger.setLevel(logging.DEBUG)      # More verbose for DB
    api_logger.setLevel(logging.INFO)      # Normal for API
    auth_logger.setLevel(logging.WARNING)  # Only warnings/errors for auth
    
    db_logger.debug("querying the database")
    db_logger.info("consultation successfully completed")
    db_logger.error("Error connecting to database!")
    
    auth_logger.debug("doing authentication")
    auth_logger.info("authentication successfully completed")
    api_logger.debug("querying the api")
    api_logger.info("consultation successfully completed")
    api_logger.error("Error querying the api")
    auth_logger.error("Auth error!")
    ```

7. 📊 JSON Format for Observability:
    ```python
    from logging_metrics import setup_file_logging
    
    # JSON logs for integration with ELK, Grafana, etc.
    logger = setup_file_logging(
        logger_name="microservice",
        log_dir="./logs",
        json_format = True
    )
    
    logger.info("User logged in", extra={"user_id": 12345, "action": "login"})
    
    # Example JSON output:
    # {
    #   "timestamp": "2024-08-05T10:30:00.123Z",
    #   "level": "INFO", 
    #   "name": "microservice",
    #   "message": "User logged in",
    #   "module": "user-api",
    #   "function": "<module>",
    #   "line": 160,
    #   "taskName": null,
    #   "user_id": 12345,
    #   "action": "login"
    # }
    ```

---

## 🏆 Best Practices

1. Configure logging once at the start:
    ```python
    # In main.py or __init__.py
    logger = setup_file_logging("my_app", log_dir="./logs")
    ```

2. Use logger hierarchy:
    ```python
    # Organize by modules/features
    db_logger = logging.getLogger("app.database")
    api_logger = logging.getLogger("app.api")
    ```

3. Different levels for console and file:
    ```python
    logger = setup_file_logging(
        console_level=logging.WARNING,  # Less verbose in console
        level=logging.DEBUG             # More detailed in the file
    )
    ```

4. Use LogTimer for critical operations:
    ```python
    with LogTimer(logger, "Complex query"):
        result = run_heavy_query()
    ```

5. Monitor metrics in long processes:
    ```python
    metrics = LogMetrics(logger)
    for batch in batches:
        with metrics.timer('batch_processing'):
            process_batch(batch)
    ```

---

## ❌ Avoid
- Configuring loggers multiple times
- Using print() instead of logger
- Excessive logging in critical loops
- Exposing sensitive information in logs
- Ignoring log file rotation

---

## 🔧 Advanced Configuration

Example of full configuration:
```python
from logging_metrics import setup_file_logging, LogMetrics
import logging

# Main configuration with all options
logger = setup_file_logging(
    logger_name="my_app",
    log_folder: str = "unknown/"
    log_dir="./logs",
    level=logging.DEBUG,
    console_level=logging.INFO,
    rotation='time',
    log_format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    date_format="%Y-%m-%d %H:%M:%S",
    max_bytes=50*1024*1024,  # 50MB
    backup_count=10,
    add_console= True
)

# Sub-module configuration
modules = ['database', 'api', 'auth', 'cache']
for module in modules:
    module_logger = logging.getLogger(f"my_app.{module}")
    module_logger.setLevel(logging.INFO)
```

---

## 🧪 Complete Example

```python
import logging
from logging_metrics import setup_file_logging, LogTimer, LogMetrics

def main():
    # Initial configuration
    logger = setup_file_logging(
        logger_name="data_processor",
        log_dir="./logs",
        console_level=logging.INFO,
        level=logging.DEBUG
    )
    
    # Sub-loggers
    db_logger = logging.getLogger("data_processor.database")
    api_logger = logging.getLogger("data_processor.api")
    
    # Metrics
    metrics = LogMetrics(logger)
    
    logger.info("Application started")
    
    try:
        # Main processing with timing
        with LogTimer(logger, "Full processing"):
            metrics.start('total_processing')
            
            # Simulate processing
            for i in range(1000):
                metrics.increment('records_processed')
                
                if i % 100 == 0:
                    logger.info(f"Processed {i} records")
                
                # Simulate occasional error
                if i % 250 == 0:
                    metrics.increment('errors_recovered')
                    logger.warning(f"Recovered error at record {i}")
            
            metrics.stop('total_processing')
            metrics.log_all()
            
        logger.info("Processing successfully completed")
        
    except Exception as e:
        logger.error(f"Error during processing: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
```

---

## 🧪 Tests

The library has a complete test suite to ensure quality and reliability.

#### Running the tests:
```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all tests
make test

# Tests with coverage
make test-cov

# Specific tests
pytest test/test_file_logging.py -v

# Tests with different verbosity levels
pytest test/ -v                     # Verbose
pytest test/ -s                     # No output capture
pytest test/ --tb=short             # Short traceback
```

#### Test Structure
```
test/
├── conftest.py                  # Shared pytest fixtures and test configurations        
├── Makefile                     # Automation commands for testing, linting, and build tasks
├── pytest.ini                   # Global pytest configuration settings
├── run_tests.py                 # Script to run all tests automatically
├── test-requirements.txt        # Development and test dependencies
├── TEST_GUIDE.md                # Quick guide: how to run and interpret tests
└── test_logging_metrics.py      # Automated tests for the logging_metrics library
```

#### Current coverage
```
# Coverage report
Name                        Stmts   Miss  Cover
-----------------------------------------------
src/logging_metrics/__init__.py     12      0   100%
src/logging_metrics/console.py      45      2    96%
src/logging_metrics/file.py         78      3    96%
src/logging_metrics/spark.py        32      1    97%
src/logging_metrics/timer.py        56      2    96%
src/logging_metrics/metrics.py      89      4    96%
-----------------------------------------------
TOTAL                            312     12    96%
```

#### Running tests in different environments
```bash
# Test in multiple Python versions with tox
pip install tox

tox

# Specific configurations
tox -e py38                # Python 3.8
tox -e py39                # Python 3.9  
tox -e py310               # Python 3.10
tox -e py311               # Python 3.11
tox -e py312               # Python 3.12
tox -e lint                # Only linting
tox -e coverage            # Only coverage
```

#### Running tests in CI/CD
Tests are run automatically in:

---


## 🔧 Requirements

Python: >= 3.8

Dependencies:

- pytz (for timezone handling)
- pyspark

---

## 📝 Changelog

v0.1.2 (Current)
- Initial stable version
- LogTimer and LogMetrics
- Spark integration
- Colored logs
- JSON log support
- Fixed file rotation bug on Windows
- Expanded documentation with more examples

---

## 🤝 Contributing

#### Contributions are welcome!
1. Fork the project
2. Create your feature branch (`git checkout -b feature/logging-metrics`)
3. Commit your changes (`git commit -m 'Add logging-metrics'`)
4. Push to the branch (`git push origin feature/logging-metrics`)
5. Open a Pull Request

---

## License

MIT License. See LICENSE for details.
