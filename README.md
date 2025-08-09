[![PyPI version](https://img.shields.io/pypi/v/logging-metrics.svg)](https://pypi.org/project/logging-metrics/)
[![Python versions](https://img.shields.io/pypi/pyversions/logging-metrics.svg)](https://pypi.org/project/logging-metrics/)
[![License](https://img.shields.io/github/license/ThaissaTeodoro/logging-metrics)](https://github.com/ThaissaTeodoro/logging-metrics/blob/main/LICENSE)
[![Build Status](https://github.com/ThaissaTeodoro/logging-metrics/actions/workflows/tests.yml/badge.svg)](https://github.com/ThaissaTeodoro/logging-metrics/actions/workflows/tests.yml)
[![Publish](https://github.com/ThaissaTeodoro/logging-metrics/actions/workflows/publish.yml/badge.svg)](https://github.com/ThaissaTeodoro/logging-metrics/actions/workflows/publish.yml)
[![codecov](https://codecov.io/gh/ThaissaTeodoro/logging-metrics/branch/main/graph/badge.svg)](https://codecov.io/gh/ThaissaTeodoro/logging-metrics)

# logging-metrics  
**Utilities Library for Logging Configuration and Management**

A library for configuring and managing logs in Python, focused on simplicity, performance, and observability — with support for PySpark integration.

---

## 📑 Table of Contents
- [✨ Features](#-features)
- [📦 Installation](#-installation)
- [📋 Functions and Classes Overview](#-functions-and-classes-overview)
- [🚀 Quick Start](#-quick-start)
- [📖 Main Features](#-main-features)
- [🏆 Best Practices](#-best-practices)
- [❌ Avoid](#-avoid)
- [🔧 Advanced Configuration](#-advanced-configuration)
- [🧪 Complete Example](#-complete-example)
- [🧪 Tests](#-tests)
- [⚙️ CI/CD](#️-cicd)
- [🔧 Requirements](#-requirements)
- [📝 Changelog](#-changelog)
- [🤝 Contributing](#-contributing)
- [📄 License](#license)

---

## ✨ Features
- 🎨 Colored logs for the terminal with different levels
- 📁 Automatic file rotation by time or size
- ⚡ PySpark DataFrame integration
- 📊 JSON format for observability systems
- ⏱️ Timing with `LogTimer`
- 📈 Metrics monitoring with `LogMetrics`
- 🔧 Hierarchical logger configuration
- 🚀 Optimized performance for critical applications

---

## 📦 Installation

**From PyPI:**
```bash
pip install logging-metrics
```

**For development:**
```bash
git clone https://github.com/ThaissaTeodoro/logging-metrics.git
cd logging-metrics
pip install -e ".[dev]"
```

---

## 📋 Functions and Classes Overview
| Name                      | Type     | Description                                                                          |
|---------------------------|----------|--------------------------------------------------------------------------------------|
| `configure_basic_logging` | Function | Configures root logger for colored console logging.                                  |
| `setup_file_logging`      | Function | Configures a logger with file output (rotation), optional console, JSON formatting.  |
| `LogTimer`                | Class    | Context manager and decorator to log execution time of code blocks or functions.     |
| `log_spark_dataframe_info`| Function | Logs schema, sample, stats of a PySpark DataFrame (row count, sample, stats, etc).   |
| `LogMetrics`              | Class    | Utility for collecting, incrementing, timing, and logging custom processing metrics. |
| `get_logger`              | Function | Returns a logger with custom handlers and caplog-friendly mode for pytest.           |

---

## 🚀 Quick Start
```python
import logging
from logging_metrics import setup_file_logging, LogTimer

logger = setup_file_logging(
    logger_name="my_app",
    log_dir="./logs",
    console_level=logging.INFO,
    level=logging.DEBUG
)

logger.info("Application started!")

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

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all tests
make test

# Tests with coverage
make test-cov
```

Test structure:
```
test/
├── conftest.py
├── pytest.ini
├── test-requirements.txt
├── test_logging_metrics.py
```

---

## ⚙️ CI/CD

This project uses **GitHub Actions** for continuous integration and delivery.

**CI Workflow (`tests.yml`):**
- Runs on push and PR to `main`/`master`.
- Steps:
  1. Install dependencies and package in editable mode.
  2. Lint code with `ruff` and `black`.
  3. Run tests with `pytest` and measure coverage.
  4. Fail build if coverage < 85%.
  5. Upload HTML coverage report and send to Codecov.

**CD Workflow (`publish.yml`):**
- Triggered on push tags `v*.*.*`.
- Steps:
  1. Build wheel and sdist.
  2. Check version tag matches `pyproject.toml`.
  3. Publish to PyPI using `TWINE_USERNAME=__token__` and `TWINE_PASSWORD` from secrets.

**Run CI locally:**
```bash
make test-ci     # Full pipeline
make test-local  # Install + tests with coverage
```

**How to publish a new version**
1. Update the version in pyproject.toml (version field).
2. Update the CHANGELOG with the release notes.
3. Create and push the tag:
 ```bash
  git add .
  git commit -m "release: v0.1.0"
  git tag -a v0.1.0 -m "release: v0.1.0"
  git push origin v0.1.0
 ```
**This will automatically trigger the publish.yml workflow, which builds the package and uploads it to PyPI.**
---

## 🔧 Requirements
- Python >= 3.8  
- Dependencies: `pytz`, `pyspark`

---

## 📝 Changelog
**v0.2.0 (Current)**
- Initial stable version
- `LogTimer` and `LogMetrics`
- Spark integration
- Colored logs
- JSON log support
- Fixed file rotation bug on Windows
- Expanded documentation with more examples

---

## 🤝 Contributing
1. Fork the project  
2. Create your feature branch  
3. Commit your changes  
4. Push to your branch  
5. Open a Pull Request  

---

## 📄 License
MIT License. See [LICENSE](LICENSE) for details.
