[![PyPI version](https://img.shields.io/pypi/v/logging-metrics.svg)](https://pypi.org/project/logging-metrics/)
[![Python versions](https://img.shields.io/pypi/pyversions/logging-metrics.svg)](https://pypi.org/project/logging-metrics/)
[![License](https://img.shields.io/github/license/ThaissaTeodoro/logging-metrics)](https://github.com/ThaissaTeodoro/logging-metrics/blob/main/LICENSE)
[![Build Status](https://github.com/ThaissaTeodoro/logging-metrics/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/ThaissaTeodoro/logging-metrics/actions/workflows/ci.yml)
[![Publish to PyPI](https://github.com/ThaissaTeodoro/logging-metrics/actions/workflows/publish-to-pypi.yml/badge.svg)](https://github.com/ThaissaTeodoro/logging-metrics/actions/workflows/publish-to-pypi.yml)
[![codecov](https://codecov.io/gh/ThaissaTeodoro/logging-metrics/branch/main/graph/badge.svg)](https://codecov.io/gh/ThaissaTeodoro/logging-metrics)

# 🎯 logging-metrics  
**Production-Ready Logging, Metrics, and Timing Library for Python**

A comprehensive, battle-tested library for logging, metrics collection, and performance timing in Python applications. Features beautiful colored console output, intelligent file rotation, decorators for timing, and Prometheus-style metrics — all with zero-configuration defaults and PySpark integration.

## 🎉 Version 1.0.0 - Production Ready!

✅ **100% Backward Compatible** - Upgrade safely without code changes  
🆕 **Enhanced Features** - More capabilities, robust error handling  
🏗️ **Modular Structure** - Clean separation with optional imports  
📚 **Complete Documentation** - Comprehensive guides and examples  
🛡️ **Production Tested** - Formal API with type safety  

---

## 📑 Table of Contents

- [✨ Key Features](#-key-features)
- [📦 Installation](#-installation)
- [🚀 Quick Start (30 seconds)](#-quick-start-30-seconds)
- [📖 Complete Usage Guide](#-complete-usage-guide)
  - [Logging](#1-logging)
  - [File Rotation](#2-file-rotation)
  - [Timing Functions](#3-timing-functions)
  - [Metrics Collection](#4-metrics-collection)
  - [PySpark Integration](#5-pyspark-integration)
- [🎨 Advanced Examples](#-advanced-examples)
- [🏆 Best Practices](#-best-practices)
- [❌ Common Pitfalls](#-common-pitfalls)
- [🔧 Configuration Reference](#-configuration-reference)
- [🆕 What's New in v1.0.0](#-whats-new-in-v100)
- [🔄 Migration Guide](#-migration-guide)
- [🐛 Troubleshooting](#-troubleshooting)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## ✨ Key Features

### 🎨 **Colored Console Logging**
Beautiful, configurable colored output for different log levels with ANSI support:
- 🔵 **DEBUG** - Cyan
- 🟢 **INFO** - Green  
- 🟡 **WARNING** - Yellow
- 🔴 **ERROR** - Red
- 🔴 **CRITICAL** - Red background (high visibility)

### 📁 **Intelligent File Rotation**
Automatic log rotation with cleanup to prevent disk space issues:
- **Time-based**: Rotate daily, hourly, weekly, or at midnight
- **Size-based**: Rotate when file reaches specified size
- **Auto-cleanup**: Automatically remove old backups (configurable retention)
- **Production-ready**: Handles edge cases and concurrent access

### ⏱️ **Performance Timing**
Measure and log function execution time with minimal code:
- **Decorators**: `@time_it` for automatic timing
- **Context managers**: Manual timing control
- **Nested support**: Track complex operations
- **Statistics**: Average, min, max execution times

### 📊 **Metrics Collection**
Prometheus-style metrics for monitoring:
- **Counters**: Track events (requests, errors, etc.)
- **Gauges**: Current values (active connections, queue size)
- **Histograms**: Value distributions
- **Timers**: Automatic timing metrics

### ⚡ **PySpark Integration**
Special support for big data workflows:
- Log DataFrame schema and statistics
- Track partition counts and sizes
- Monitor transformations
- Performance profiling

### 🔧 **Zero Configuration**
Works out-of-the-box with sensible defaults:
```python
from logging_metrics import get_logger
logger = get_logger("app")
logger.info("It just works!")
```

---

## 📦 Installation

### Basic Installation

```bash
pip install logging-metrics
```

### With Optional Dependencies

```bash
# For PySpark integration
pip install logging-metrics[spark]

# For development (testing, linting, etc.)
pip install logging-metrics[dev]

# Install everything
pip install logging-metrics[all]
```

### From Source (Development)

```bash
git clone https://github.com/ThaissaTeodoro/logging-metrics.git
cd logging-metrics
pip install -e ".[dev]"
```

### Requirements

- **Python**: 3.8 or higher
- **Core dependencies**: pytz (timezone support)
- **Optional**: pyspark (for PySpark integration)

---

## 🚀 Quick Start (30 seconds)

### 1. Basic Logging

```python
from logging_metrics import get_logger

# Create logger
logger = get_logger("my_app")

# Start logging!
logger.info("Application started")
logger.warning("Low disk space")
logger.error("Connection failed")
```

**Output:**
```
2026-02-28 10:30:15 [INFO] my_app - Application started
2026-02-28 10:30:16 [WARNING] my_app - Low disk space
2026-02-28 10:30:17 [ERROR] my_app - Connection failed
```

### 2. Colored Console

```python
from logging_metrics import get_logger, create_console_handler
import logging

logger = get_logger("app")
console = create_console_handler(level=logging.INFO, use_colors=True)
logger.addHandler(console)

logger.info("✅ Success")      # Green
logger.warning("⚠️ Warning")   # Yellow
logger.error("❌ Error")       # Red
```

### 3. File Logging with Rotation

```python
from logging_metrics import setup_file_logging

# Automatic rotation + cleanup
logger = setup_file_logging(
    logger_name="my_app",
    log_dir="./logs",
    rotation="time",        # Rotate daily
    backup_count=30         # Keep 30 days
)

logger.info("Logged to file with auto-rotation!")
```

**Result:** Creates `./logs/my_app.log` with automatic daily rotation and 30-day retention.

### 4. Time Functions

```python
from logging_metrics import time_it, get_logger

logger = get_logger("app")

@time_it(logger)
def process_data(data):
    # Your code here
    return result

# Automatically logs execution time
process_data(my_data)
```

**Output:**
```
2026-02-28 10:30:15 [INFO] app - process_data executed in 1.234s
```

### 5. Metrics Collection

```python
from logging_metrics import LogMetrics

metrics = LogMetrics("api")

# Track events
metrics.increment_counter("requests")
metrics.set_gauge("active_connections", 42)
metrics.record_histogram("response_time_ms", 150)

# View metrics
print(metrics.get_summary())
```

**Output:**
```
Metrics Summary for 'api':
  Counters:
    requests: 1
  Gauges:
    active_connections: 42
  Histograms:
    response_time_ms: count=1, avg=150.00
```

---

## 📖 Complete Usage Guide

### 1. Logging

#### 1.1 Basic Logger

```python
from logging_metrics import get_logger
import logging

# Create logger with specific level
logger = get_logger("my_app", level=logging.DEBUG)

# All log levels
logger.debug("Debug information")
logger.info("Informational message")
logger.warning("Warning message")
logger.error("Error occurred")
logger.critical("Critical issue!")

# With variables
user_id = 12345
logger.info(f"User {user_id} logged in")

# With exception info
try:
    risky_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
```

#### 1.2 Colored Console Handler

```python
from logging_metrics import get_logger, create_console_handler
import logging

logger = get_logger("app")

# Create colored console handler
console_handler = create_console_handler(
    level=logging.INFO,
    use_colors=True,  # Enable ANSI colors
    timezone="America/Sao_Paulo"  # Optional: set timezone
)

logger.addHandler(console_handler)

# Colorful output!
logger.debug("Debug info")        # Cyan (not shown if level=INFO)
logger.info("Information")        # Green
logger.warning("Be careful")      # Yellow
logger.error("Something wrong")   # Red
logger.critical("URGENT!")        # Red background + bold
```

**Console Output (with colors):**
```
2026-02-28 10:30:15 [INFO] app - Information        (in green)
2026-02-28 10:30:16 [WARNING] app - Be careful      (in yellow)
2026-02-28 10:30:17 [ERROR] app - Something wrong   (in red)
2026-02-28 10:30:18 [CRITICAL] app - URGENT!        (red bg + white bold)
```

#### 1.3 JSON Logging (for Log Aggregation)

```python
from logging_metrics import get_logger, JSONFormatter, create_file_handler

logger = get_logger("api")

# Create JSON formatter
json_formatter = JSONFormatter()

# Create file handler with JSON
file_handler = create_file_handler(
    log_file="./logs/api.json",
    max_bytes=10485760,  # 10 MB
    backup_count=5
)
file_handler.setFormatter(json_formatter)
logger.addHandler(file_handler)

# Logs are now in JSON format
logger.info("User login", extra={"user_id": 123, "ip": "192.168.1.1"})
```

**Output in `api.json`:**
```json
{
  "timestamp": "2026-02-28T10:30:15.123456",
  "level": "INFO",
  "logger": "api",
  "message": "User login",
  "user_id": 123,
  "ip": "192.168.1.1"
}
```

#### 1.4 Custom Formatters

```python
import logging
from logging_metrics import get_logger, ColoredFormatter

logger = get_logger("app")

# Create custom formatter
custom_formatter = ColoredFormatter(
    fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    use_colors=True
)

# Apply to console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(custom_formatter)
logger.addHandler(console_handler)

logger.info("Custom formatted message")
```

**Output:**
```
2026-02-28 10:30:15 | INFO     | app | Custom formatted message
```

---

### 2. File Rotation

#### 2.1 Time-Based Rotation (Recommended for Production)

```python
from logging_metrics import create_timed_file_handler, get_logger
import logging

logger = get_logger("app")

# Daily rotation at midnight
daily_handler = create_timed_file_handler(
    log_file="./logs/app.log",
    when="midnight",      # Rotate at midnight
    interval=1,           # Every 1 day
    backup_count=30       # Keep 30 days (RECOMMENDED for production)
)

logger.addHandler(daily_handler)
logger.info("Application started")
```

**What happens:**
- Creates `app.log` (current log file)
- At midnight: renames to `app.log.2026-02-28`, creates new `app.log`
- After 30 days: automatically deletes `app.log.2026-01-29`

**File Structure After 30+ Days:**
```
logs/
├── app.log                    ← Current (today)
├── app.log.2026-02-27        ← Yesterday
├── app.log.2026-02-26        ← 2 days ago
├── ... (28 more files)
└── app.log.2026-01-29        ← 30 days ago (oldest kept)
```

#### 2.2 Hourly Rotation (High-Volume Applications)

```python
hourly_handler = create_timed_file_handler(
    log_file="./logs/api.log",
    when="H",           # Hourly rotation
    interval=1,         # Every 1 hour
    backup_count=168    # Keep 7 days (24h × 7 = 168)
)
```

#### 2.3 Weekly Rotation (Low-Volume Applications)

```python
weekly_handler = create_timed_file_handler(
    log_file="./logs/batch.log",
    when="W0",          # Every Monday (W0-W6 for Mon-Sun)
    interval=1,
    backup_count=52     # Keep 1 year (52 weeks)
)
```

#### 2.4 Size-Based Rotation (Predictable Disk Usage)

```python
from logging_metrics import create_file_handler

size_handler = create_file_handler(
    log_file="./logs/app.log",
    max_bytes=10485760,    # 10 MB per file
    backup_count=10        # Keep 10 files = ~100 MB total
)

logger.addHandler(size_handler)
```

**What happens:**
- Creates `app.log`
- When reaches 10 MB: renames to `app.log.1`, creates new `app.log`
- When next reaches 10 MB: renames current to `app.log.1`, old `.1` to `.2`
- After 10 files: deletes `app.log.10` (oldest)

#### 2.5 Combined: Multiple Handlers

```python
from logging_metrics import get_logger, create_timed_file_handler, create_file_handler
import logging

logger = get_logger("app")

# General logs: daily rotation
general_handler = create_timed_file_handler(
    "./logs/app.log",
    when="midnight",
    backup_count=30
)
logger.addHandler(general_handler)

# Error logs: size-based, separate file
error_handler = create_file_handler(
    "./logs/errors.log",
    max_bytes=5242880,  # 5 MB
    backup_count=20
)
error_handler.setLevel(logging.ERROR)  # Only errors
logger.addHandler(error_handler)

# Now:
logger.info("This goes to app.log")
logger.error("This goes to BOTH app.log AND errors.log")
```

#### 2.6 Complete File Logging Setup (One Function)

```python
from logging_metrics import setup_file_logging

# All-in-one configuration
logger = setup_file_logging(
    logger_name="my_app",
    log_dir="./logs",
    console_level=logging.INFO,
    level=logging.DEBUG,
    rotation="time",        # or "size"
    backup_count=30,        # Keep 30 days/files
    json_format=False,      # Set True for JSON
    timezone="UTC"
)

# Ready to use!
logger.info("Logging configured!")
```

**Creates:**
```
logs/
└── my_app.log (with automatic rotation)
```

---

### 3. Timing Functions

#### 3.1 Function Decorator (Simplest)

```python
from logging_metrics import time_it, get_logger

logger = get_logger("app")

@time_it(logger)
def fetch_data(url):
    response = requests.get(url)
    return response.json()

@time_it(logger, level="DEBUG")  # Custom log level
def process_item(item):
    # Processing logic
    return processed

# Automatically logs execution time
data = fetch_data("https://api.example.com/data")
result = process_item(data)
```

**Output:**
```
2026-02-28 10:30:15 [INFO] app - fetch_data executed in 0.523s
2026-02-28 10:30:16 [DEBUG] app - process_item executed in 0.012s
```

#### 3.2 Context Manager (More Control)

```python
from logging_metrics import LogTimer, get_logger

logger = get_logger("app")

# Measure specific code blocks
def complex_operation():
    with LogTimer(logger, "Database query"):
        result = db.query("SELECT * FROM large_table")
    
    with LogTimer(logger, "Data transformation"):
        transformed = transform(result)
    
    with LogTimer(logger, "File export"):
        export_to_file(transformed, "output.csv")
    
    return transformed

complex_operation()
```

**Output:**
```
2026-02-28 10:30:15 [INFO] app - Database query executed in 2.345s
2026-02-28 10:30:17 [INFO] app - Data transformation executed in 1.123s
2026-02-28 10:30:18 [INFO] app - File export executed in 0.456s
```

#### 3.3 Nested Timing

```python
from logging_metrics import LogTimer, get_logger

logger = get_logger("pipeline")

def data_pipeline():
    with LogTimer(logger, "Full pipeline"):
        # Step 1
        with LogTimer(logger, "  → Extract"):
            data = extract_data()
        
        # Step 2
        with LogTimer(logger, "  → Transform"):
            transformed = transform(data)
        
        # Step 3
        with LogTimer(logger, "  → Load"):
            load_to_db(transformed)

data_pipeline()
```

**Output:**
```
2026-02-28 10:30:15 [INFO] pipeline -   → Extract executed in 1.234s
2026-02-28 10:30:16 [INFO] pipeline -   → Transform executed in 2.345s
2026-02-28 10:30:18 [INFO] pipeline -   → Load executed in 0.567s
2026-02-28 10:30:19 [INFO] pipeline - Full pipeline executed in 4.146s
```

#### 3.4 Silent Timing (Return Value)

```python
from logging_metrics import LogTimer
import logging

# Measure without logging
with LogTimer(None, "Silent operation") as timer:
    # Your code
    process_data()

# Access elapsed time
print(f"Processing took {timer.elapsed:.2f} seconds")

# Conditional logging
if timer.elapsed > 5.0:
    logger.warning(f"Slow operation: {timer.elapsed:.2f}s")
```

---

### 4. Metrics Collection

#### 4.1 Counters (Track Events)

```python
from logging_metrics import LogMetrics

metrics = LogMetrics("api")

# Count events
metrics.increment_counter("requests_total")
metrics.increment_counter("requests_total")  # Now 2
metrics.increment_counter("errors_total")

# Increment by custom amount
metrics.increment_counter("bytes_sent", 1024)

# View counters
print(metrics.get_counter("requests_total"))  # Output: 2
```

#### 4.2 Gauges (Current Values)

```python
metrics = LogMetrics("system")

# Set current value
metrics.set_gauge("active_connections", 42)
metrics.set_gauge("queue_size", 128)
metrics.set_gauge("cpu_usage_percent", 75.5)

# Update gauge
metrics.set_gauge("active_connections", 45)  # Now 45

# Retrieve gauge
connections = metrics.get_gauge("active_connections")
print(f"Active connections: {connections}")
```

#### 4.3 Histograms (Value Distributions)

```python
metrics = LogMetrics("requests")

# Record values
metrics.record_histogram("response_time_ms", 120)
metrics.record_histogram("response_time_ms", 95)
metrics.record_histogram("response_time_ms", 150)
metrics.record_histogram("response_time_ms", 105)

# Get statistics
histogram = metrics.get_histogram("response_time_ms")
print(f"Count: {histogram['count']}")
print(f"Average: {histogram['avg']:.2f}ms")
print(f"Min: {histogram['min']}ms")
print(f"Max: {histogram['max']}ms")
print(f"Total: {histogram['sum']}ms")
```

**Output:**
```
Count: 4
Average: 117.50ms
Min: 95ms
Max: 150ms
Total: 470ms
```

#### 4.4 Timers (Automatic Timing Metrics)

```python
from logging_metrics import LogMetrics, get_logger

metrics = LogMetrics("app")
logger = get_logger("app")

# Start timer
metrics.start_timer("database_query")

# Do work
result = db.query("SELECT * FROM users")

# Stop timer (automatically records to histogram)
metrics.stop_timer("database_query")

# Measure multiple operations
for i in range(10):
    metrics.start_timer("api_call")
    response = api.call()
    metrics.stop_timer("api_call")

# View statistics
timer_stats = metrics.get_histogram("api_call")
logger.info(f"API calls: avg={timer_stats['avg']:.2f}ms")
```

#### 4.5 Context Manager for Timing

```python
from logging_metrics import LogMetrics

metrics = LogMetrics("operations")

# Automatic timing
with metrics.timer("file_processing"):
    process_large_file("data.csv")

# Timer is automatically recorded
stats = metrics.get_histogram("file_processing")
print(f"File processing: {stats['avg']:.2f}s average")
```

#### 4.6 Complete Metrics Summary

```python
from logging_metrics import LogMetrics

metrics = LogMetrics("application")

# Track various metrics
metrics.increment_counter("requests", 1523)
metrics.increment_counter("errors", 12)
metrics.set_gauge("active_users", 342)
metrics.record_histogram("response_time", 125)

# Get comprehensive summary
summary = metrics.get_summary()
print(summary)
```

**Output:**
```
======================================
Metrics Summary for 'application'
======================================

Counters:
  requests: 1523
  errors: 12

Gauges:
  active_users: 342

Histograms:
  response_time:
    count: 1
    sum: 125.00
    avg: 125.00
    min: 125.00
    max: 125.00

======================================
```

#### 4.7 Real-World Example: API Monitoring

```python
from logging_metrics import LogMetrics, get_logger
from flask import Flask, request
import time

app = Flask(__name__)
metrics = LogMetrics("api")
logger = get_logger("api")

@app.before_request
def before_request():
    request.start_time = time.time()
    metrics.increment_counter("requests_total")
    metrics.set_gauge("active_requests", 
                     metrics.get_gauge("active_requests", 0) + 1)

@app.after_request
def after_request(response):
    # Record response time
    elapsed = (time.time() - request.start_time) * 1000
    metrics.record_histogram("response_time_ms", elapsed)
    
    # Update metrics
    metrics.set_gauge("active_requests",
                     metrics.get_gauge("active_requests") - 1)
    metrics.increment_counter(f"status_{response.status_code}")
    
    # Log slow requests
    if elapsed > 1000:
        logger.warning(f"Slow request: {request.path} took {elapsed:.0f}ms")
    
    return response

@app.route("/metrics")
def metrics_endpoint():
    return metrics.get_summary()

# Now you have comprehensive API monitoring!
```

---

### 5. PySpark Integration

#### 5.1 Log DataFrame Info

```python
from logging_metrics import log_spark_dataframe_info, get_logger
from pyspark.sql import SparkSession

logger = get_logger("spark_job")
spark = SparkSession.builder.getOrCreate()

# Load data
df = spark.read.parquet("data/users.parquet")

# Log comprehensive DataFrame information
log_spark_dataframe_info(
    df=df,
    logger=logger,
    df_name="users",
    show_sample=True,      # Show sample rows
    sample_rows=5,         # How many rows to show
    log_level=logging.INFO
)
```

**Output:**
```
2026-02-28 10:30:15 [INFO] spark_job - DataFrame 'users' Analysis:
2026-02-28 10:30:15 [INFO] spark_job - Columns: 8
2026-02-28 10:30:15 [INFO] spark_job - Schema:
  ├─ user_id (bigint)
  ├─ name (string)
  ├─ email (string)
  ├─ age (int)
  ├─ city (string)
  ├─ country (string)
  ├─ created_at (timestamp)
  └─ updated_at (timestamp)
2026-02-28 10:30:15 [INFO] spark_job - Row count: 1,523,842
2026-02-28 10:30:15 [INFO] spark_job - Partitions: 200
2026-02-28 10:30:15 [INFO] spark_job - Sample (first 5 rows):
  +-------+-------------+-------------------+---+----------+---------+-------------------+
  |user_id|name         |email              |age|city      |country  |created_at         |
  +-------+-------------+-------------------+---+----------+---------+-------------------+
  |1      |John Doe     |john@example.com   |32 |São Paulo |Brazil   |2025-01-15 10:30:00|
  |2      |Jane Smith   |jane@example.com   |28 |New York  |USA      |2025-01-16 11:45:00|
  ...
```

#### 5.2 Track Transformations

```python
from logging_metrics import LogTimer, get_logger

logger = get_logger("etl")

# Time each transformation
with LogTimer(logger, "Load raw data"):
    df_raw = spark.read.parquet("data/raw/")

with LogTimer(logger, "Clean data"):
    df_clean = df_raw.filter(col("age") > 0).dropDuplicates()

with LogTimer(logger, "Aggregate"):
    df_agg = df_clean.groupBy("country").agg(
        count("*").alias("user_count"),
        avg("age").alias("avg_age")
    )

with LogTimer(logger, "Write results"):
    df_agg.write.mode("overwrite").parquet("data/output/")
```

#### 5.3 Monitor Data Quality

```python
from pyspark.sql.functions import col, count, when
from logging_metrics import get_logger

logger = get_logger("data_quality")

def check_data_quality(df, name):
    total_rows = df.count()
    
    # Check for nulls
    for column in df.columns:
        null_count = df.filter(col(column).isNull()).count()
        null_pct = (null_count / total_rows) * 100
        
        if null_pct > 5:
            logger.warning(
                f"{name}.{column}: {null_pct:.2f}% null values ({null_count}/{total_rows})"
            )
        else:
            logger.info(
                f"{name}.{column}: {null_pct:.2f}% null values ✓"
            )

# Use it
check_data_quality(df_users, "users")
```

---

## 🎨 Advanced Examples

### Complete Application Setup

```python
"""
Production-ready logging setup for a web application
"""
from logging_metrics import (
    get_logger,
    create_console_handler,
    create_timed_file_handler,
    create_file_handler,
    LogMetrics,
    time_it
)
import logging

def setup_logging(app_name="app", log_dir="./logs"):
    """Setup comprehensive logging for production"""
    
    logger = get_logger(app_name, level=logging.DEBUG)
    
    # 1. Console handler (for development/debugging)
    console = create_console_handler(
        level=logging.INFO,
        use_colors=True
    )
    logger.addHandler(console)
    
    # 2. General log file (daily rotation)
    general_handler = create_timed_file_handler(
        log_file=f"{log_dir}/{app_name}.log",
        when="midnight",
        backup_count=30,  # 30 days retention
        level=logging.DEBUG
    )
    logger.addHandler(general_handler)
    
    # 3. Error log file (separate, size-based)
    error_handler = create_file_handler(
        log_file=f"{log_dir}/{app_name}_errors.log",
        max_bytes=10485760,  # 10 MB
        backup_count=20
    )
    error_handler.setLevel(logging.ERROR)
    logger.addHandler(error_handler)
    
    return logger

# Initialize
logger = setup_logging("my_api")
metrics = LogMetrics("my_api")

# Use throughout your application
@time_it(logger)
def handle_request(request_id):
    metrics.increment_counter("requests")
    logger.info(f"Handling request {request_id}")
    
    try:
        result = process_request()
        metrics.increment_counter("success")
        return result
    except Exception as e:
        metrics.increment_counter("errors")
        logger.error(f"Request failed: {e}", exc_info=True)
        raise
```

### Microservice with Full Observability

```python
from logging_metrics import get_logger, setup_file_logging, LogMetrics, LogTimer
from flask import Flask, request, jsonify
import time

app = Flask(__name__)
logger = setup_file_logging("api", "./logs", rotation="time", backup_count=30)
metrics = LogMetrics("api")

@app.before_request
def start_request():
    request.start_time = time.time()
    request.request_id = generate_request_id()
    
    logger.info(f"[{request.request_id}] {request.method} {request.path}")
    metrics.increment_counter("requests_total")
    metrics.increment_counter(f"requests_{request.method}")

@app.after_request
def end_request(response):
    elapsed_ms = (time.time() - request.start_time) * 1000
    
    metrics.record_histogram("response_time_ms", elapsed_ms)
    metrics.increment_counter(f"status_{response.status_code}")
    
    logger.info(
        f"[{request.request_id}] {response.status_code} "
        f"in {elapsed_ms:.2f}ms"
    )
    
    return response

@app.route("/api/users", methods=["GET"])
def get_users():
    with LogTimer(logger, "Database query"):
        users = db.query("SELECT * FROM users")
    
    return jsonify(users)

@app.route("/metrics")
def metrics_endpoint():
    return metrics.get_summary()

if __name__ == "__main__":
    logger.info("Starting API server")
    app.run()
```

### ETL Pipeline with Monitoring

```python
from logging_metrics import get_logger, LogTimer, LogMetrics
from pyspark.sql import SparkSession

logger = get_logger("etl")
metrics = LogMetrics("etl")

def run_etl_pipeline():
    spark = SparkSession.builder.appName("ETL").getOrCreate()
    
    logger.info("="*60)
    logger.info("Starting ETL Pipeline")
    logger.info("="*60)
    
    try:
        # Extract
        with LogTimer(logger, "Extract phase") as extract_timer:
            df_raw = spark.read.parquet("s3://data/raw/")
            row_count = df_raw.count()
            logger.info(f"Loaded {row_count:,} rows")
            metrics.set_gauge("rows_extracted", row_count)
        
        # Transform
        with LogTimer(logger, "Transform phase") as transform_timer:
            df_clean = (df_raw
                .filter(col("valid") == True)
                .dropDuplicates(["id"])
                .withColumn("processed_at", current_timestamp())
            )
            clean_count = df_clean.count()
            logger.info(f"Cleaned to {clean_count:,} rows")
            metrics.set_gauge("rows_transformed", clean_count)
        
        # Load
        with LogTimer(logger, "Load phase") as load_timer:
            df_clean.write.mode("overwrite").parquet("s3://data/processed/")
            logger.info("Data written successfully")
        
        # Summary
        total_time = (extract_timer.elapsed + 
                     transform_timer.elapsed + 
                     load_timer.elapsed)
        
        logger.info("="*60)
        logger.info("ETL Pipeline Completed Successfully")
        logger.info(f"Total time: {total_time:.2f}s")
        logger.info(f"Rows processed: {clean_count:,}")
        logger.info(f"Throughput: {clean_count/total_time:.0f} rows/sec")
        logger.info("="*60)
        
        metrics.increment_counter("pipeline_success")
        
    except Exception as e:
        logger.error(f"ETL Pipeline failed: {e}", exc_info=True)
        metrics.increment_counter("pipeline_failures")
        raise
    
    finally:
        spark.stop()

if __name__ == "__main__":
    run_etl_pipeline()
```

---

## 🏆 Best Practices

### 1. Logger Naming Convention

```python
# ✅ GOOD: Use hierarchical names
logger = get_logger("myapp.api.users")
logger = get_logger("myapp.database.connection")
logger = get_logger("myapp.cache.redis")

# ❌ AVOID: Flat names
logger = get_logger("users")
logger = get_logger("db")
```

**Why?** Hierarchical names allow filtering and level control:
```python
# Set different levels for different components
logging.getLogger("myapp.api").setLevel(logging.INFO)
logging.getLogger("myapp.database").setLevel(logging.DEBUG)
```

### 2. Log Rotation Settings

```python
# ✅ PRODUCTION: Time-based with 30+ day retention
handler = create_timed_file_handler(
    "app.log",
    when="midnight",
    backup_count=30  # Keep 30 days minimum
)

# ✅ HIGH-VOLUME: Size-based with predictable disk usage
handler = create_file_handler(
    "app.log",
    max_bytes=104857600,  # 100 MB
    backup_count=10       # 10 files = ~1 GB total
)

# ❌ AVOID: Too few backups
backup_count=3  # Only 3 days - may lose important logs!
```

### 3. Log Levels

Use appropriate log levels:

```python
# DEBUG: Detailed diagnostic info (disabled in production)
logger.debug(f"SQL query: {query}")
logger.debug(f"Variable state: x={x}, y={y}")

# INFO: General informational messages
logger.info("User logged in successfully")
logger.info("Processing batch 1 of 10")

# WARNING: Something unexpected but not an error
logger.warning("API rate limit approaching")
logger.warning("Cache miss - fetching from database")

# ERROR: An error occurred but application can continue
logger.error(f"Failed to send email to {user}", exc_info=True)
logger.error("Database connection lost, retrying...")

# CRITICAL: Serious error, application may not continue
logger.critical("Out of memory!")
logger.critical("All database connections failed")
```

### 4. Exception Logging

```python
# ✅ GOOD: Include exception info
try:
    risky_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
    # exc_info=True includes full stack trace

# ✅ GOOD: Specific exceptions
try:
    value = int(user_input)
except ValueError as e:
    logger.warning(f"Invalid input from user: {user_input}")
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)

# ❌ AVOID: Silent failures
try:
    risky_operation()
except:
    pass  # Never do this!
```

### 5. Metrics Naming

```python
# ✅ GOOD: Clear, descriptive names with units
metrics.increment_counter("requests_total")
metrics.record_histogram("response_time_ms")
metrics.set_gauge("active_connections_count")
metrics.record_histogram("payload_size_bytes")

# ❌ AVOID: Ambiguous names
metrics.increment_counter("count")
metrics.record_histogram("time")
metrics.set_gauge("value")
```

### 6. Performance Considerations

```python
# ✅ GOOD: Use lazy formatting
logger.debug("Processing %s with %d items", name, count)

# ❌ AVOID: Eager string formatting for debug logs
logger.debug(f"Processing {expensive_operation()} items")
# expensive_operation() runs even if DEBUG is disabled!

# ✅ GOOD: Check level first for expensive operations
if logger.isEnabledFor(logging.DEBUG):
    logger.debug(f"Detailed state: {expensive_dump()}")
```

### 7. Sensitive Data

```python
# ❌ NEVER log sensitive data
logger.info(f"User login: {password}")  # NO!
logger.info(f"Credit card: {cc_number}")  # NO!
logger.info(f"API key: {api_key}")  # NO!

# ✅ GOOD: Mask or omit sensitive data
logger.info(f"User login: {username}")  # OK
logger.info(f"Card ending: ...{cc_number[-4:]}")  # OK
logger.info(f"API key: {api_key[:8]}...")  # OK
```

---

## ❌ Common Pitfalls

### 1. File Rotation Not Working

**Problem:**
```python
# This creates files with timestamps in the name!
# 20260228_103015-app.log
# 20260228_110015-app.log
# TimedRotatingFileHandler can't recognize these as related!

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
handler = create_timed_file_handler(f"{timestamp}-app.log")
```

**Solution:**
```python
# Use consistent base filename
handler = create_timed_file_handler("app.log")
# Creates: app.log, app.log.2026-02-27, app.log.2026-02-26, etc
```

### 2. Too Many Log Files Accumulated

**Problem:**
```python
# Default backup_count is too small!
handler = create_timed_file_handler("app.log")  # Only keeps 7 days
```

**Solution:**
```python
# Set appropriate retention for production
handler = create_timed_file_handler(
    "app.log",
    backup_count=30  # Keep 30 days minimum
)
```

### 3. Logs Not Appearing

**Problem:**
```python
logger = get_logger("app")
# Forgot to add handler!
logger.info("This won't appear anywhere")
```

**Solution:**
```python
logger = get_logger("app")
console = create_console_handler()
logger.addHandler(console)
logger.info("Now it works!")

# Or use all-in-one setup
logger = setup_file_logging("app", "./logs")
```

### 4. Duplicate Log Messages

**Problem:**
```python
# Adding handlers multiple times
for i in range(3):
    logger.addHandler(console_handler)
# Now every log appears 3 times!
```

**Solution:**
```python
# Check if handler already exists
if not logger.handlers:
    logger.addHandler(console_handler)

# Or clear handlers first
logger.handlers.clear()
logger.addHandler(console_handler)
```

### 5. Timing Decorator on Generator

**Problem:**
```python
@time_it(logger)
def generate_items():
    for i in range(1000):
        yield i  # Timing only measures generator creation, not execution!
```

**Solution:**
```python
@time_it(logger)
def generate_and_consume():
    items = generate_items()
    return list(items)  # Force evaluation

# Or use manual timing
with LogTimer(logger, "Generate items"):
    items = list(generate_items())
```

---

## 🔧 Configuration Reference

### create_timed_file_handler Parameters

```python
create_timed_file_handler(
    log_file: str | Path,           # Path to log file
    when: str = "midnight",         # When to rotate
    interval: int = 1,              # Rotation interval
    backup_count: int = 7,          # Number of backups to keep
    encoding: str = "utf-8",        # File encoding
    formatter: Formatter = None,    # Custom formatter
    level: int = logging.DEBUG      # Minimum log level
)
```

**`when` options:**
- `"S"` - Seconds
- `"M"` - Minutes
- `"H"` - Hours
- `"D"` - Days
- `"midnight"` - Rotate at midnight (recommended)
- `"W0"` to `"W6"` - Specific weekday (0=Monday, 6=Sunday)

### create_file_handler Parameters

```python
create_file_handler(
    log_file: str | Path,           # Path to log file
    max_bytes: int = 10485760,      # Max file size (10 MB default)
    backup_count: int = 5,          # Number of backups
    encoding: str = "utf-8",        # File encoding
    formatter: Formatter = None,    # Custom formatter
    level: int = logging.DEBUG      # Minimum log level
)
```

### setup_file_logging Parameters

```python
setup_file_logging(
    logger_name: str,               # Logger name
    log_dir: str = "./logs",        # Log directory
    console_level: int = logging.INFO,     # Console log level
    level: int = logging.DEBUG,     # File log level
    rotation: str = "time",         # "time" or "size"
    backup_count: int = 5,          # Backups to keep
    json_format: bool = False,      # Use JSON format
    timezone: str = "UTC"           # Timezone for timestamps
)
```

---

## 🆕 What's New in v1.0.0

### ✨ New Features

1. **Modular imports**: Import only what you need
```python
from logging_metrics.logger import get_logger
from logging_metrics.timers import LogTimer
from logging_metrics.metrics import LogMetrics
```

2. **Enhanced error handling**: All functions now have proper error handling and validation

3. **Type hints**: Full type annotation support for better IDE integration

4. **Improved documentation**: Comprehensive docstrings and examples

### 🔄 API Changes (Backward Compatible)

All existing code continues to work:
```python
# v0.x.x (still works)
from logging_metrics import get_logger, time_it, LogMetrics

# v1.0.0 (new, optional)
from logging_metrics.logger import get_logger
from logging_metrics.timers import time_it
from logging_metrics.metrics import LogMetrics
```

### 🐛 Bug Fixes

1. Fixed timestamp in log filenames preventing rotation (see issue #12)
2. Improved timezone handling in formatters
3. Fixed metrics serialization for Prometheus export

---

## 🔄 Migration Guide

### Upgrading from v0.x.x to v1.0.0

**Good news: No code changes required!** v1.0.0 is 100% backward compatible.

#### Optional: Use New Modular Structure

```python
# Old (still works)
from logging_metrics import get_logger, LogTimer, LogMetrics

# New (optional, more explicit)
from logging_metrics.logger import get_logger, setup_file_logging
from logging_metrics.timers import LogTimer, time_it
from logging_metrics.metrics import LogMetrics
```

#### Update Dependencies

```bash
pip install --upgrade logging-metrics
```

#### Review Log File Names

If you were using `setup_file_logging()`, check your log files:

**Before v1.0.0:**
```
logs/20260228_103015-app.log
logs/20260227_093000-app.log
```

**After v1.0.0:**
```
logs/app.log
logs/app.log.2026-02-27
```

**Action:** Clean up old log files with timestamps in names (see cleanup script in troubleshooting section).

---

## 🐛 Troubleshooting

### Log Files Not Rotating

**Symptom:** Files accumulate with timestamps in names (e.g., `20260228_app.log`)

**Cause:** Old version created files with timestamps preventing rotation

**Solution:**
```bash
# Clean up old files
cd logs/
rm 202*-*.log

# Update library
pip install --upgrade logging-metrics

# New files will rotate correctly
```

### Disk Space Issues

**Symptom:** Log directory consuming too much disk space

**Solution:**
```python
# Increase backup_count (more retention)
handler = create_timed_file_handler(
    "app.log",
    backup_count=30  # Instead of default 7
)

# Or use size-based rotation for predictable usage
handler = create_file_handler(
    "app.log",
    max_bytes=104857600,  # 100 MB per file
    backup_count=10       # 10 files = ~1 GB total
)
```

### Colors Not Showing in Console

**Symptom:** ANSI escape codes visible instead of colors

**Cause:** Terminal doesn't support ANSI colors or colors disabled

**Solution:**
```python
# Disable colors
console = create_console_handler(use_colors=False)

# Or check terminal support
import sys
if sys.stdout.isatty():
    console = create_console_handler(use_colors=True)
else:
    console = create_console_handler(use_colors=False)
```

### Metrics Not Accumulating

**Symptom:** Metrics reset or don't accumulate as expected

**Cause:** Creating new `LogMetrics` instance each time

**Solution:**
```python
# ❌ WRONG: New instance each time
def handle_request():
    metrics = LogMetrics("api")  # Creates new instance!
    metrics.increment_counter("requests")

# ✅ CORRECT: Reuse same instance
metrics = LogMetrics("api")  # Create once

def handle_request():
    metrics.increment_counter("requests")  # Reuse
```

### Permission Denied on Log Files

**Symptom:** `PermissionError: [Errno 13] Permission denied: './logs/app.log'`

**Solution:**
```bash
# Check directory permissions
chmod 755 ./logs

# Or specify user-writable location
handler = create_timed_file_handler(
    "~/.local/share/myapp/app.log",  # User home
    # or
    "/tmp/myapp/app.log"  # Temp directory
)
```

---

## 🤝 Contributing

We welcome contributions! Here's how:

### Development Setup

```bash
# Clone repository
git clone https://github.com/ThaissaTeodoro/logging-metrics.git
cd logging-metrics

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
flake8 src/
black src/ --check

# Run type checking
mypy src/
```

### Submitting Changes

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/my-feature`
3. **Make your changes** with tests
4. **Run tests**: `pytest`
5. **Run linters**: `black src/ && flake8 src/`
6. **Commit**: `git commit -m "Add my feature"`
7. **Push**: `git push origin feature/my-feature`
8. **Create Pull Request**

### Guidelines

- Add tests for new features
- Update documentation
- Follow PEP 8 style guide
- Add type hints
- Include docstrings

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with ❤️ by [Thaissa Teodoro](https://github.com/ThaissaTeodoro)
- Inspired by Python's standard `logging` module
- Metrics design inspired by Prometheus

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/ThaissaTeodoro/logging-metrics/issues)
- **Documentation**: [Full API Reference](https://logging-metrics.readthedocs.io/)
- **PyPI**: [logging-metrics](https://pypi.org/project/logging-metrics/)

---

## 📊 Quick Reference Card

```python
# === LOGGING ===
from logging_metrics import get_logger, create_console_handler

logger = get_logger("app")
console = create_console_handler(use_colors=True)
logger.addHandler(console)

logger.debug("Debug")      # Cyan
logger.info("Info")        # Green
logger.warning("Warning")  # Yellow
logger.error("Error")      # Red

# === FILE ROTATION ===
from logging_metrics import create_timed_file_handler

handler = create_timed_file_handler(
    "app.log",
    when="midnight",
    backup_count=30
)
logger.addHandler(handler)

# === TIMING ===
from logging_metrics import time_it, LogTimer

@time_it(logger)
def my_function():
    pass

with LogTimer(logger, "Operation"):
    # code here
    pass

# === METRICS ===
from logging_metrics import LogMetrics

metrics = LogMetrics("app")
metrics.increment_counter("requests")
metrics.set_gauge("connections", 42)
metrics.record_histogram("latency_ms", 150)
print(metrics.get_summary())

# === ALL-IN-ONE ===
from logging_metrics import setup_file_logging

logger = setup_file_logging(
    "app",
    log_dir="./logs",
    rotation="time",
    backup_count=30
)
```

---

**Made with ❤️ for Python developers who care about observability** 🚀

