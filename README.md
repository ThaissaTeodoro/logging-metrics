[![PyPI version](https://img.shields.io/pypi/v/logging-metrics.svg)](https://pypi.org/project/logging-metrics/)
[![Python versions](https://img.shields.io/pypi/pyversions/logging-metrics.svg)](https://pypi.org/project/logging-metrics/)
[![License](https://img.shields.io/github/license/ThaissaTeodoro/logging-metrics)](https://github.com/ThaissaTeodoro/logging-metrics/blob/main/LICENSE)
[![Build Status](https://github.com/ThaissaTeodoro/logging-metrics/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/ThaissaTeodoro/logging-metrics/actions/workflows/ci.yml)
[![Publish to PyPI](https://github.com/ThaissaTeodoro/logging-metrics/actions/workflows/publish-to-pypi.yml/badge.svg)](https://github.com/ThaissaTeodoro/logging-metrics/actions/workflows/publish-to-pypi.yml)
[![codecov](https://codecov.io/gh/ThaissaTeodoro/logging-metrics/branch/main/graph/badge.svg)](https://codecov.io/gh/ThaissaTeodoro/logging-metrics)
[![GPG Signed](https://img.shields.io/badge/commits-GPG%20signed-blue?logo=gnuprivacyguard)](https://github.com/ThaissaTeodoro/logging-metrics/commits?author=ThaissaTeodoro)

# logging-metrics  
**Production-Ready Logging Utilities Library for Python**

A comprehensive library for configuring and managing logs in Python, focused on simplicity, performance, and observability — with support for PySpark integration and advanced metrics collection.

## 🎉 **Version 1.0.0 - Production Ready!**

✅ **100% Backward Compatible** - Your existing code continues to work  
🆕 **Enhanced Features** - New capabilities and robust error handling  
🏗️ **Modular Structure** - Better organization with optional imports  
📚 **Complete Documentation** - Comprehensive API documentation  
🛡️ **Production Ready** - Formal API, error handling, and type safety  

---

## 📑 Table of Contents
- [✨ Features](#-features)
- [📦 Installation](#-installation)
- [🚨 Compatibility Notice](#-compatibility-notice)
- [🏗️ Modular Structure](#️-modular-structure)
- [📋 API Overview](#-api-overview)
- [🚀 Quick Start](#-quick-start)
- [📖 Main Features](#-main-features)
- [🆕 New in v1.0.0](#-new-in-v100)
- [🏆 Best Practices](#-best-practices)
- [❌ Common Pitfalls](#-common-pitfalls)
- [🔧 Advanced Configuration](#-advanced-configuration)
- [🧪 Complete Examples](#-complete-examples)
- [🧪 Testing](#-testing)
- [⚙️ CI/CD](#️-cicd)
- [🔧 Requirements](#-requirements)
- [📝 Changelog](#-changelog)
- [🔄 Migration Guide](#-migration-guide)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## ✨ Features
- 🎨 **Colored logs** for terminal with different severity levels
- 📁 **Automatic file rotation** by time or size with configurable retention
- ⚡ **PySpark DataFrame integration** with comprehensive analysis
- 📊 **JSON format** for observability systems (ELK, Grafana, etc.)
- ⏱️ **Advanced timing** with `LogTimer` (context manager + decorator)
- 📈 **Comprehensive metrics** with `LogMetrics` (counters, values, timers)
- 🔧 **Hierarchical logger configuration** for modular applications
- 🚀 **Production-ready** with robust error handling and type safety
- 🏗️ **Modular architecture** with clean separation of concerns
- 📚 **Complete API documentation** with examples and type hints

---

## 📦 Installation

### **From PyPI (Recommended):**
```bash
pip install logging-metrics
```

### **With Optional Dependencies:**
```bash
# For PySpark integration
pip install logging-metrics[spark]

# For development
pip install logging-metrics[dev]

# Everything
pip install logging-metrics[all]
```

### **For Development:**
```bash
git clone https://github.com/ThaissaTeodoro/logging-metrics.git
cd logging-metrics
pip install -e ".[dev]"
```

---

## 🚨 **Compatibility Notice**

### 🎉 **Great News: 100% Backward Compatible!**

If you're upgrading from v0.x.x, **no code changes are required**. Your existing imports and usage patterns will continue to work exactly as before.

### 🆕 **Optional: New Modular Structure**

Starting with v1.0.0, you can optionally use more specific imports for better organization:

```python
# ✅ Your existing code (still works perfectly)
from logging_metrics import setup_file_logging, LogTimer, LogMetrics

# 🆕 New modular imports (optional, for better organization)
from logging_metrics.logger import setup_file_logging
from logging_metrics.timers import LogTimer
from logging_metrics.metrics import LogMetrics

# 🔄 Full compatibility fallback
from logging_metrics.core import setup_file_logging, LogTimer, LogMetrics
```

📖 **Need help migrating?** See our [Migration Guide](https://github.com/ThaissaTeodoro/logging-metrics/MIGRATION_GUIDE.md) for detailed information.

---

## 🏗️ **Modular Structure**

Starting with v1.0.0, the library is organized into specialized modules:

| Module | Functionality | When to Use |
|--------|----------------|-------------|
| `logger.py` | Formatters, handlers, configuration | Basic logging setup |
| `timers.py` | `LogTimer` for execution timing | Performance monitoring |
| `metrics.py` | `LogMetrics` for data collection | Application metrics |
| `core.py` | Backward compatibility | Gradual migration |

### **Import Options:**

```python
# Traditional (100% compatible)
from logging_metrics import setup_file_logging, LogTimer, LogMetrics

# Modular (recommended for new projects)
from logging_metrics.logger import setup_file_logging
from logging_metrics.timers import LogTimer
from logging_metrics.metrics import LogMetrics

# Compatibility (always works)
from logging_metrics.core import setup_file_logging, LogTimer, LogMetrics
```

---

## 📋 **API Overview**

| Name | Module | Type | Description |
|------|--------|------|-------------|
| `setup_file_logging` | `logger` | Function | Complete logging setup with file rotation and console |
| `configure_basic_logging` | `logger` | Function | Simple console logging with colors |
| `get_logger` | `logger` | Function | Flexible logger creation with custom handlers |
| `LogTimer` | `timers` | Class | Context manager and decorator for execution timing |
| `LogMetrics` | `metrics` | Class | Comprehensive metrics collection and logging |
| `log_spark_dataframe_info` | `logger` | Function | PySpark DataFrame analysis and logging |
| `ColoredFormatter` | `logger` | Class | ANSI color formatter for console output |
| `JSONFormatter` | `logger` | Class | JSON formatter for structured logging |

### **Flexible Import Strategy:**
- **Modular**: `from logging_metrics.logger import setup_file_logging`
- **Traditional**: `from logging_metrics import setup_file_logging`
- **Compatibility**: `from logging_metrics.core import setup_file_logging`

---

## 🚀 Quick Start

### **Simple Console Logging**
```python
from logging_metrics import configure_basic_logging

logger = configure_basic_logging()
logger.debug("Debug message")     # Gray
logger.info("Info message")       # Green  
logger.warning("Warning")         # Yellow
logger.error("Error occurred")    # Red
logger.critical("Critical issue") # Bold red
```

### **Production File Logging**
```python
from logging_metrics import setup_file_logging, LogTimer

logger = setup_file_logging(
    logger_name="my_app",
    log_dir="./logs",
    console_level=logging.INFO,
    level=logging.DEBUG,
    json_format=True  # For production monitoring
)

logger.info("Application started!")

with LogTimer(logger, "Critical operation"):
    # Your code here
    result = perform_complex_operation()
```

### **Modular Imports (New in v1.0.0)**
```python
from logging_metrics.logger import setup_file_logging
from logging_metrics.timers import LogTimer  
from logging_metrics.metrics import LogMetrics

logger = setup_file_logging("my_app")
metrics = LogMetrics(logger)

with metrics.timer('startup'):
    initialize_application()

metrics.log_all()
```

---

## 📖 Main Features

### **1. Colored Console Logging**
```python
from logging_metrics import configure_basic_logging

logger = configure_basic_logging()
logger.debug("Debug message")     # Gray
logger.info("Info")               # Green  
logger.warning("Warning")         # Yellow
logger.error("Error")             # Red
logger.critical("Critical")       # Bold red background
```

### **2. Automatic Log Rotation**
```python
from logging_metrics import setup_file_logging

# Size-based rotation
logger = setup_file_logging(
    logger_name="app",
    log_dir="./logs",
    max_bytes=10*1024*1024,  # 10MB
    backup_count=10,
    rotation='size'
)

# Time-based rotation (daily)
logger = setup_file_logging(
    logger_name="app", 
    log_dir="./logs",
    rotation='time',
    backup_count=30  # Keep 30 days
)
```

### **3. PySpark Integration**
```python
from pyspark.sql import SparkSession
from logging_metrics import configure_basic_logging, log_spark_dataframe_info

spark = SparkSession.builder.getOrCreate()
df = spark.createDataFrame([(1, "Ana"), (2, "Bruno")], ["id", "name"])

logger = configure_basic_logging()

log_spark_dataframe_info(
    df=df,
    logger=logger, 
    name="users_data",
    show_schema=True,
    show_sample=True,
    sample_rows=5
)
```

### **4. Advanced Timing with LogTimer**
```python
from logging_metrics import LogTimer, configure_basic_logging

logger = configure_basic_logging()

# As a context manager
with LogTimer(logger, "Database query"):
    result = database.execute("SELECT * FROM users")

# As a decorator
@LogTimer.as_decorator(logger, "Data processing")
def process_data(data):
    return data.transform()

# Manual control (new in v1.0.0)
timer = LogTimer(logger, "Manual operation")
timer.start()
# ... perform work ...
elapsed = timer.stop()
```

### **5. Comprehensive Metrics Collection**
```python
from logging_metrics import LogMetrics, configure_basic_logging

logger = configure_basic_logging()
metrics = LogMetrics(logger)

# Counters
metrics.increment('requests_processed')
metrics.increment('errors', 2)

# Values
metrics.set('current_users', 1250)
metrics.set('status', 'healthy')

# Timers with context manager
with metrics.timer('database_operation'):
    result = database.query("SELECT * FROM users")

# Log everything
metrics.log_all()
```

### **6. Hierarchical Logger Configuration**
```python
from logging_metrics import setup_file_logging
import logging

# Main application logger
main_logger = setup_file_logging("my_app", log_dir="./logs")

# Specialized sub-loggers
db_logger = logging.getLogger("my_app.database")
api_logger = logging.getLogger("my_app.api")
auth_logger = logging.getLogger("my_app.auth")

# Configure levels per module
db_logger.setLevel(logging.DEBUG)      # Verbose for database
api_logger.setLevel(logging.INFO)      # Normal for API
auth_logger.setLevel(logging.WARNING)  # Only warnings for auth

db_logger.debug("Executing query: SELECT * FROM users")
api_logger.info("API request processed successfully")
auth_logger.warning("Failed login attempt from IP: 192.168.1.100")
```

### **7. JSON Format for Observability**
```python
from logging_metrics import setup_file_logging

# JSON logs for ELK Stack, Grafana, etc.
logger = setup_file_logging(
    logger_name="microservice",
    log_dir="./logs",
    json_format=True
)

logger.info("User action", extra={
    "user_id": 12345, 
    "action": "login",
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0..."
})

# Output (formatted for readability):
# {
#   "timestamp": "2025-08-16T10:30:00.123Z",
#   "level": "INFO", 
#   "name": "microservice",
#   "message": "User action",
#   "module": "user_service",
#   "function": "handle_login",
#   "line": 45,
#   "user_id": 12345,
#   "action": "login",
#   "ip_address": "192.168.1.100",
#   "user_agent": "Mozilla/5.0..."
# }
```

---

## 🆕 **New in v1.0.0**

### **Enhanced LogMetrics**
```python
from logging_metrics.metrics import LogMetrics

metrics = LogMetrics(logger)
metrics.increment('requests', 100)
metrics.set('status', 'healthy')

# 🆕 NEW: Programmatic access
count = metrics.get_counter('requests')  # Returns 100
status = metrics.get_value('status', 'unknown')  # Returns 'healthy'

# 🆕 NEW: Check existence
if metrics.has_metric('requests'):
    print("Request counter exists")

# 🆕 NEW: List all metrics
all_metrics = metrics.list_metrics()
print(f"Counters: {all_metrics['counters']}")

# 🆕 NEW: Get comprehensive summary
summary = metrics.get_summary()
print(f"Total requests: {summary['counters']['requests']}")

# 🆕 NEW: Reset everything
metrics.reset()  # Clear all counters, values, and timers

# 🆕 NEW: String representation
print(metrics)  # LogMetrics(counters=3, values=2, timers=1 [1 completed, 0 active])
```

### **Enhanced LogTimer**
```python
from logging_metrics.timers import LogTimer

timer = LogTimer(logger, "Operation")

# 🆕 NEW: Manual control
timer.start()
current_time = timer.elapsed()  # Get current elapsed time
elapsed = timer.stop()

# 🆕 NEW: String representation
print(timer)  # LogTimer(operation='Operation', status=running, elapsed=1.234s)
```

### **Version Information**
```python
from logging_metrics import __version__, get_version, get_version_info

print(f"Version: {get_version()}")  # "1.0.0"
major, minor, patch = get_version_info()  # (1, 0, 0)
```

### **Context Manager for Metrics**
```python
# 🆕 NEW: Automatic timing context manager
with metrics.timer('database_operation'):
    result = db.query("SELECT * FROM users")
# Timer automatically started and stopped
```

---

## 🏆 Best Practices

### **1. Configure Logging Once at Startup**
```python
# In main.py or __init__.py
from logging_metrics import setup_file_logging

logger = setup_file_logging(
    logger_name="my_app", 
    log_dir="./logs",
    console_level=logging.INFO,  # Less verbose in console
    level=logging.DEBUG,         # More detailed in files
    json_format=True            # For production
)
```

### **2. Use Hierarchical Logger Names**
```python
# Organize by modules/features
db_logger = logging.getLogger("myapp.database")
api_logger = logging.getLogger("myapp.api")
auth_logger = logging.getLogger("myapp.authentication")
cache_logger = logging.getLogger("myapp.cache")
```

### **3. Different Log Levels for Different Outputs**
```python
logger = setup_file_logging(
    logger_name="production_app",
    console_level=logging.WARNING,  # Only warnings/errors in console
    level=logging.DEBUG,           # Everything in files
    add_console=True
)
```

### **4. Use LogTimer for Performance Critical Operations**
```python
from logging_metrics.timers import LogTimer

# For database queries
with LogTimer(logger, "User lookup query"):
    user = db.query("SELECT * FROM users WHERE id = ?", user_id)

# For API calls
@LogTimer.as_decorator(logger, "External API call")
def fetch_user_data(user_id):
    return external_api.get_user(user_id)
```

### **5. Monitor Business Metrics with LogMetrics**
```python
from logging_metrics.metrics import LogMetrics

metrics = LogMetrics(logger)

# Track business KPIs
metrics.increment('daily_signups')
metrics.increment('successful_payments')
metrics.set('active_users', get_active_user_count())

# Performance metrics
with metrics.timer('order_processing'):
    process_order(order_data)

# Regular reporting
metrics.log_all()  # Log summary every hour/day
```

### **6. Use Modular Imports for Large Projects**
```python
# config/logging_config.py
from logging_metrics.logger import setup_file_logging, get_logger

# services/metrics_service.py  
from logging_metrics.metrics import LogMetrics

# utils/timing.py
from logging_metrics.timers import LogTimer
```

---

## ❌ **Common Pitfalls to Avoid**

### **Don't:**
- ❌ Configure loggers multiple times in the same application
- ❌ Use `print()` instead of proper logging
- ❌ Log sensitive information (passwords, tokens, PII)
- ❌ Ignore log file rotation (can fill disk space)
- ❌ Use overly verbose logging in production critical paths
- ❌ Create loggers without proper naming hierarchy

### **Do:**
- ✅ Configure logging once at application startup
- ✅ Use appropriate log levels (DEBUG for development, INFO+ for production)
- ✅ Implement log rotation to manage disk space
- ✅ Use structured logging (JSON) for production systems
- ✅ Monitor log volumes and adjust levels as needed
- ✅ Use hierarchical logger names for better organization

---

## 🔧 Advanced Configuration

### **Complete Production Setup**
```python
from logging_metrics import setup_file_logging, LogMetrics
import logging

# Main configuration with all production features
logger = setup_file_logging(
    logger_name="production_app",
    log_dir="/var/log/myapp",
    level=logging.INFO,                     # File level
    console_level=logging.WARNING,          # Console level
    rotation='time',                        # Daily rotation
    backup_count=30,                        # Keep 30 days
    json_format=True,                       # Structured logs
    log_format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    date_format="%Y-%m-%d %H:%M:%S",
    utc="UTC",                             # Use UTC for production
    max_bytes=100*1024*1024,               # 100MB max file size
    add_console=True                        # Console output enabled
)

# Configure specialized loggers
modules = ['database', 'api', 'auth', 'cache', 'scheduler']
for module in modules:
    module_logger = logging.getLogger(f"production_app.{module}")
    module_logger.setLevel(logging.INFO)

# Setup application metrics
metrics = LogMetrics(logger)
```

### **Development vs Production Configuration**
```python
import os
from logging_metrics import setup_file_logging
import logging

# Environment-based configuration
ENV = os.getenv('ENVIRONMENT', 'development')

if ENV == 'production':
    logger = setup_file_logging(
        logger_name="myapp",
        log_dir="/var/log/myapp",
        level=logging.INFO,
        console_level=logging.ERROR,
        json_format=True,
        rotation='time',
        backup_count=30
    )
elif ENV == 'staging':
    logger = setup_file_logging(
        logger_name="myapp",
        log_dir="./logs",
        level=logging.DEBUG,
        console_level=logging.INFO,
        json_format=True,
        rotation='size',
        backup_count=10
    )
else:  # development
    logger = setup_file_logging(
        logger_name="myapp",
        log_dir="./logs",
        level=logging.DEBUG,
        console_level=logging.DEBUG,
        json_format=False,  # Human-readable for dev
        rotation='size',
        backup_count=3
    )
```

### **Custom Formatters and Handlers**
```python
from logging_metrics import (
    ColoredFormatter, 
    JSONFormatter,
    create_file_handler,
    create_console_handler,
    get_logger
)

# Custom formatter for special requirements
class CustomFormatter(ColoredFormatter):
    def format(self, record):
        # Add custom fields
        record.app_version = "1.0.0"
        record.environment = os.getenv('ENV', 'dev')
        return super().format(record)

# Create custom handlers
file_handler = create_file_handler(
    log_file="./logs/custom.log",
    max_bytes=50*1024*1024,
    backup_count=5,
    formatter=JSONFormatter()
)

console_handler = create_console_handler(
    level=logging.INFO,
    formatter=CustomFormatter(),
    use_colors=True
)

# Create logger with custom handlers
logger = get_logger(
    name="custom_app",
    level=logging.DEBUG,
    handlers=[file_handler, console_handler],
    propagate=False
)
```

### **Microservice Configuration with Environment Variables**
```python
import os
from logging_metrics import setup_file_logging, LogMetrics
import logging

def get_microservice_config():
    """Production-ready microservice logging configuration."""
    return {
        'service_name': os.getenv('SERVICE_NAME', 'unknown-service'),
        'environment': os.getenv('ENVIRONMENT', 'development'),
        'log_level': os.getenv('LOG_LEVEL', 'INFO'),
        'log_dir': os.getenv('LOG_DIR', './logs'),
        'json_format': os.getenv('JSON_LOGS', 'true').lower() == 'true',
        'rotation': os.getenv('LOG_ROTATION', 'time'),
        'backup_count': int(os.getenv('LOG_BACKUP_COUNT', '30'))
    }

def setup_microservice_logging():
    """Configure logging for microservice deployment."""
    config = get_microservice_config()
    
    logger = setup_file_logging(
        logger_name=config['service_name'],
        log_dir=config['log_dir'],
        level=getattr(logging, config['log_level'].upper()),
        console_level=logging.WARNING if config['environment'] == 'production' else logging.INFO,
        json_format=config['json_format'],
        rotation=config['rotation'],
        backup_count=config['backup_count'],
        utc="UTC"
    )
    
    # Configure service-specific loggers
    request_logger = logging.getLogger(f"{config['service_name']}.requests")
    db_logger = logging.getLogger(f"{config['service_name']}.database")
    
    return logger, LogMetrics(logger)

# Usage in Docker/Kubernetes
logger, metrics = setup_microservice_logging()
```

---

## 🧪 Complete Examples

### **Example 1: Microservice Logging Setup**
```python
from logging_metrics import setup_file_logging, LogMetrics, LogTimer
import logging
import os
from datetime import datetime

def setup_microservice_logging():
    """Complete microservice logging configuration."""
    service_name = os.getenv('SERVICE_NAME', 'unknown-service')
    environment = os.getenv('ENVIRONMENT', 'development')
    
    # Main service logger
    logger = setup_file_logging(
        logger_name=service_name,
        log_dir=f"/var/log/{service_name}",
        level=logging.INFO if environment == 'production' else logging.DEBUG,
        console_level=logging.WARNING,
        json_format=True,
        rotation='time',
        backup_count=30,
        utc="UTC"
    )
    
    # Specialized loggers
    request_logger = logging.getLogger(f"{service_name}.requests")
    db_logger = logging.getLogger(f"{service_name}.database")
    external_logger = logging.getLogger(f"{service_name}.external")
    
    # Configure levels per component
    request_logger.setLevel(logging.INFO)
    db_logger.setLevel(logging.DEBUG if environment != 'production' else logging.INFO)
    external_logger.setLevel(logging.INFO)
    
    # Setup metrics collection
    metrics = LogMetrics(logger)
    
    return logger, metrics

def process_request(request_data):
    """Example request processing with comprehensive logging."""
    logger, metrics = setup_microservice_logging()
    request_id = request_data.get('id', 'unknown')
    
    # Log request start
    logger.info("Processing request", extra={
        "request_id": request_id,
        "endpoint": request_data.get('endpoint'),
        "user_id": request_data.get('user_id'),
        "timestamp": datetime.utcnow().isoformat()
    })
    
    # Increment request counter
    metrics.increment('requests_total')
    metrics.increment(f'requests_{request_data.get("endpoint", "unknown")}')
    
    try:
        with LogTimer(logger, f"Request {request_id}"):
            # Database operation
            with metrics.timer('database_query'):
                db_result = database.query(request_data)
                metrics.increment('database_queries')
            
            # External API call
            with metrics.timer('external_api'):
                api_result = external_service.call(db_result)
                metrics.increment('external_calls')
            
            # Update success metrics
            metrics.increment('requests_successful')
            metrics.set('last_successful_request', request_id)
            
            logger.info("Request completed successfully", extra={
                "request_id": request_id,
                "records_processed": len(db_result),
                "response_size": len(api_result),
                "success": True
            })
            
            return api_result
            
    except Exception as e:
        # Error handling with metrics
        metrics.increment('requests_failed')
        metrics.increment(f'errors_{type(e).__name__}')
        
        logger.error("Request failed", extra={
            "request_id": request_id,
            "error_type": type(e).__name__,
            "error_message": str(e),
            "success": False
        }, exc_info=True)
        
        raise
    
    finally:
        # Log metrics summary periodically
        if metrics.get_counter('requests_total') % 100 == 0:
            metrics.log_all()
```

### **Example 2: Data Processing Pipeline**
```python
from logging_metrics import setup_file_logging, LogMetrics, LogTimer
from logging_metrics import log_spark_dataframe_info
import logging
from datetime import datetime

def setup_data_pipeline():
    """Data processing pipeline with comprehensive monitoring."""
    
    # Setup pipeline logging
    logger = setup_file_logging(
        logger_name="data_pipeline",
        log_dir="./logs/pipeline",
        level=logging.DEBUG,
        console_level=logging.INFO,
        json_format=True,
        rotation='time'
    )
    
    # Component loggers
    ingestion_logger = logging.getLogger("data_pipeline.ingestion")
    transform_logger = logging.getLogger("data_pipeline.transform")
    validation_logger = logging.getLogger("data_pipeline.validation")
    output_logger = logging.getLogger("data_pipeline.output")
    
    # Metrics collection
    metrics = LogMetrics(logger)
    
    return logger, metrics

def process_data_batch(batch_id, source_data):
    """Process a data batch with full observability."""
    logger, metrics = setup_data_pipeline()
    
    logger.info("Starting batch processing", extra={
        "batch_id": batch_id,
        "source_records": len(source_data),
        "batch_size": len(source_data),
        "start_time": datetime.utcnow().isoformat()
    })
    
    metrics.set('current_batch_id', batch_id)
    metrics.set('batch_start_time', datetime.utcnow().isoformat())
    
    try:
        with LogTimer(logger, f"Batch {batch_id} processing"):
            metrics.start('total_processing_time')
            
            # 1. Data Ingestion
            with metrics.timer('ingestion_time'):
                logger.info("Starting data ingestion")
                ingested_data = ingest_data(source_data)
                metrics.increment('batches_ingested')
                metrics.set('ingested_records', len(ingested_data))
                
                logger.info("Ingestion completed", extra={
                    "records_ingested": len(ingested_data),
                    "ingestion_rate": len(ingested_data) / metrics.get_timer_elapsed('ingestion_time'),
                    "data_quality_score": calculate_quality_score(ingested_data)
                })
            
            # 2. Data Transformation
            with metrics.timer('transformation_time'):
                logger.info("Starting data transformation")
                transformed_data = transform_data(ingested_data)
                metrics.increment('batches_transformed')
                metrics.set('transformed_records', len(transformed_data))
                
                transformation_ratio = len(transformed_data) / len(ingested_data)
                metrics.set('transformation_ratio', transformation_ratio)
                
                logger.info("Transformation completed", extra={
                    "records_transformed": len(transformed_data),
                    "transformation_ratio": transformation_ratio,
                    "transformation_rate": len(transformed_data) / metrics.get_timer_elapsed('transformation_time')
                })
            
            # 3. Data Validation
            with metrics.timer('validation_time'):
                logger.info("Starting data validation")
                validation_results = validate_data(transformed_data)
                
                valid_records = sum(1 for r in validation_results if r['valid'])
                invalid_records = len(validation_results) - valid_records
                
                metrics.set('valid_records', valid_records)
                metrics.set('invalid_records', invalid_records)
                metrics.increment('batches_validated')
                
                if invalid_records > 0:
                    logger.warning("Data validation issues found", extra={
                        "valid_records": valid_records,
                        "invalid_records": invalid_records,
                        "validation_success_rate": valid_records / len(validation_results)
                    })
                    metrics.increment('validation_warnings')
            
            # 4. Output Generation
            with metrics.timer('output_time'):
                logger.info("Generating output")
                output_path = generate_output(transformed_data, batch_id)
                metrics.increment('batches_completed')
                metrics.set('output_path', output_path)
                
                logger.info("Output generated successfully", extra={
                    "output_path": output_path,
                    "output_size": get_file_size(output_path),
                    "final_record_count": len(transformed_data)
                })
            
            # Final metrics
            total_time = metrics.stop('total_processing_time')
            throughput = len(source_data) / total_time
            
            metrics.set('batch_throughput', throughput)
            metrics.set('batch_success', True)
            
            logger.info("Batch processing completed successfully", extra={
                "batch_id": batch_id,
                "total_processing_time": total_time,
                "throughput_records_per_second": throughput,
                "final_status": "success"
            })
            
            # Log comprehensive metrics
            metrics.log_all()
            
            return {
                "status": "success",
                "batch_id": batch_id,
                "records_processed": len(transformed_data),
                "processing_time": total_time,
                "output_path": output_path
            }
            
    except Exception as e:
        # Error handling
        metrics.increment('batches_failed')
        metrics.set('batch_success', False)
        metrics.set('error_type', type(e).__name__)
        
        logger.error("Batch processing failed", extra={
            "batch_id": batch_id,
            "error_type": type(e).__name__,
            "error_message": str(e),
            "processing_stage": get_current_stage()
        }, exc_info=True)
        
        # Still log metrics for analysis
        metrics.log_all()
        
        raise
    
    finally:
        # Cleanup resources
        cleanup_batch_resources(batch_id)
```

### **Example 3: Web Application Integration**
```python
from flask import Flask, request, g
from logging_metrics import setup_file_logging, LogMetrics, LogTimer
import logging
import time
import uuid

app = Flask(__name__)

# Setup application logging
logger = setup_file_logging(
    logger_name="web_app",
    log_dir="./logs/webapp",
    level=logging.INFO,
    console_level=logging.INFO,
    json_format=True
)

# Global metrics instance
metrics = LogMetrics(logger)

def generate_request_id():
    """Generate unique request ID."""
    return str(uuid.uuid4())

@app.before_request
def before_request():
    """Log request start and setup timing."""
    g.start_time = time.time()
    g.request_id = generate_request_id()
    
    # Log request start
    logger.info("Request started", extra={
        "request_id": g.request_id,
        "method": request.method,
        "path": request.path,
        "user_agent": request.headers.get('User-Agent'),
        "remote_addr": request.remote_addr,
        "content_length": request.content_length
    })
    
    # Increment request metrics
    metrics.increment('http_requests_total')
    metrics.increment(f'http_requests_{request.method.lower()}')

@app.after_request
def after_request(response):
    """Log request completion and metrics."""
    duration = time.time() - g.start_time
    
    # Log request completion
    logger.info("Request completed", extra={
        "request_id": g.request_id,
        "status_code": response.status_code,
        "duration_ms": duration * 1000,
        "response_size": len(response.get_data())
    })
    
    # Update metrics
    metrics.increment(f'http_responses_{response.status_code}')
    if response.status_code >= 400:
        metrics.increment('http_errors_total')
    
    # Track response times
    metrics.set('last_request_duration', duration)
    
    return response

@app.route('/api/users')
def get_users():
    """Example API endpoint with comprehensive logging."""
    with LogTimer(logger, f"GET /api/users - {g.request_id}"):
        try:
            # Database query
            with metrics.timer('database_query'):
                users = database.get_all_users()
                metrics.increment('database_queries')
            
            # Business logic
            with metrics.timer('user_processing'):
                processed_users = process_users(users)
                metrics.set('active_users_count', len(processed_users))
            
            logger.info("Users retrieved successfully", extra={
                "request_id": g.request_id,
                "user_count": len(processed_users),
                "query_time": metrics.get_timer_elapsed('database_query')
            })
            
            return {"users": processed_users, "count": len(processed_users)}
            
        except Exception as e:
            logger.error("Failed to retrieve users", extra={
                "request_id": g.request_id,
                "error_type": type(e).__name__,
                "error_message": str(e)
            }, exc_info=True)
            
            metrics.increment('api_errors')
            raise

# Metrics endpoint for monitoring
@app.route('/metrics')
def get_metrics():
    """Endpoint to expose application metrics."""
    summary = metrics.get_summary()
    return {
        "counters": summary["counters"],
        "values": summary["values"],
        "completed_timers": summary["completed_timers"],
        "timestamp": time.time()
    }

# Health check endpoint
@app.route('/health')
def health_check():
    """Health check endpoint."""
    logger.info("Health check requested", extra={"request_id": g.request_id})
    return {"status": "healthy", "timestamp": time.time()}

if __name__ == '__main__':
    # Log metrics summary every 5 minutes
    import threading
    
    def periodic_metrics():
        while True:
            time.sleep(300)  # 5 minutes
            metrics.log_all()
    
    metrics_thread = threading.Thread(target=periodic_metrics, daemon=True)
    metrics_thread.start()
    
    logger.info("Web application starting")
    app.run(debug=False, host='0.0.0.0', port=5000)
```

---

## 🧪 Testing

The library includes a comprehensive test suite to ensure quality and reliability.

### **Running Tests**
```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test categories
make test-unit        # Unit tests only
make test-integration # Integration tests only
pytest -m spark       # Spark-specific tests
```

### **Test Structure**
```
test/
├── conftest.py                 # Pytest configuration and fixtures
├── pytest.ini                 # Test settings and markers
├── test-requirements.txt       # Test dependencies
├── test_logger.py              # Comprehensive test suite for the logger module
├── test_metrics.py             # Comprehensive test suite for the metrics module
├── test_timers.py              # Comprehensive test suite for the timers module
└── TEST_GUIDE.md              # Testing documentation
```

### **Test Categories**
- **Unit Tests**: Individual function and class testing
- **Integration Tests**: End-to-end workflow testing  
- **Error Tests**: Error handling and edge cases
- **Performance Tests**: Timing and overhead validation
- **Spark Tests**: PySpark integration (when available)

### **Writing Tests with pytest Integration**
```python
import pytest
from logging_metrics import get_logger, LogMetrics

def test_my_application_feature(caplog):
    """Test with logging-metrics and pytest caplog."""
    # Use caplog-friendly logger
    logger = get_logger("test_app", caplog_friendly=True)
    metrics = LogMetrics(logger)
    
    # Your test code
    with caplog.at_level(logging.INFO):
        my_application_function(logger, metrics)
    
    # Verify logging
    assert "Expected message" in caplog.text
    assert metrics.get_counter('test_counter') == 1

def test_timing_operations(caplog):
    """Test timing functionality."""
    logger = get_logger("timing_test", caplog_friendly=True)
    
    with caplog.at_level(logging.INFO):
        with LogTimer(logger, "Test operation"):
            time.sleep(0.01)
    
    messages = [record.getMessage() for record in caplog.records]
    assert any("Starting: Test operation" in msg for msg in messages)
    assert any("Completed: Test operation" in msg for msg in messages)
```

---

## ⚙️ CI/CD

This project uses **GitHub Actions** for continuous integration and automated publishing.

### **CI Workflow** (`ci.yml`)
- **Triggers**: Push and PR to `main`/`master`
- **Python Versions**: 3.9, 3.10, 3.11, 3.12
- **Steps**:
  1. Install dependencies and package in editable mode
  2. Run code quality checks (ruff, black, mypy)
  3. Execute comprehensive test suite with coverage
  4. Enforce minimum 85% coverage threshold
  5. Upload coverage reports to Codecov

### **CD Workflow** (`publish-to-pypi.yml`)
- **Triggers**: Version tags (`v*.*.*`)
- **Steps**:
  1. Build wheel and source distribution
  2. Validate package integrity
  3. Verify tag matches `pyproject.toml` version
  4. Publish to PyPI via OIDC (secure, no tokens needed)

### **Running CI Locally**
```bash
# Full CI pipeline
make test-ci

# Individual steps
make install     # Install dependencies
make test-cov    # Tests with coverage
make lint        # Code quality checks
make format      # Code formatting
```

### **Release Process**
```bash
# 1. Update version in pyproject.toml
# 2. Update CHANGELOG.md
# 3. Create and push tag
git add .
git commit -m "release: v1.0.0"
git tag -a v1.0.0 -m "release: v1.0.0 - Production Ready"
git push origin v1.0.0

# GitHub Actions automatically:
# - Builds the package
# - Runs all tests
# - Publishes to PyPI
```

---

## 🔧 Requirements

### **Runtime Requirements**
- **Python**: >= 3.9
- **Dependencies**: 
  - `pytz>=2023.3,<2025.0` (timezone support)

### **Optional Dependencies**
- **PySpark**: `pyspark>=3.3.0,<5.0.0` (for DataFrame integration)

### **Development Requirements**
- **Testing**: `pytest>=7.0.0`, `pytest-cov>=4.0.0`
- **Code Quality**: `black>=22.0.0`, `ruff>=0.1.0`, `mypy>=1.0.0`
- **Type Checking**: Full type hints included

### **System Requirements**
- **File System**: Write permissions for log directories
- **Memory**: Minimal overhead (< 1MB base usage)
- **Performance**: < 1ms overhead per log operation

---

## 📝 Changelog

### **v1.0.0 (Current) - Production Ready** 🎉
- ✨ **Formal Public API**: Defined with comprehensive documentation
- 🛡️ **Robust Error Handling**: Input validation and meaningful error messages
- 🏗️ **Modular Structure**: Better organization with backward compatibility
- 📚 **Complete Documentation**: Google-style docstrings and type hints
- 🆕 **Enhanced LogMetrics**: New methods for programmatic access
- ⚡ **Enhanced LogTimer**: Manual control and better error handling
- 🔢 **Version Information**: `__version__`, `get_version()` functions
- 🧪 **Comprehensive Tests**: 85%+ coverage with edge cases
- 📦 **Stable Dependencies**: Pinned version ranges for reliability

### **v0.2.3 (Previous)**
- Initial stable version with core functionality
- `LogTimer` and `LogMetrics` basic implementation
- Spark integration and colored logs
- JSON format support and file rotation

**[View Full Changelog](https://github.com/ThaissaTeodoro/CHANGELOG.md)**

---

## 🔄 **Migration Guide**

### **From v0.x.x to v1.0.0**

**✅ No Breaking Changes**: Your existing code will continue to work exactly as before!

```python
# Your existing code (still works perfectly):
from logging_metrics import setup_file_logging, LogTimer, LogMetrics

# Optional: New modular structure (for better organization):
from logging_metrics.logger import setup_file_logging
from logging_metrics.timers import LogTimer
from logging_metrics.metrics import LogMetrics

# New v1.0.0 features you can optionally use:
metrics = LogMetrics(logger)
summary = metrics.get_summary()  # Programmatic access
metrics.reset()                  # Clear all metrics
count = metrics.get_counter('requests')  # Get current value
```

**📖 Detailed Migration Information**: [MIGRATION_GUIDE.md](https://github.com/ThaissaTeodoro/MIGRATION_GUIDE.md)

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### **Development Setup**
```bash
# Clone repository
git clone https://github.com/ThaissaTeodoro/logging-metrics.git
cd logging-metrics

# Install in development mode
pip install -e ".[dev]"

# Run tests to verify setup
make test
```

### **Contribution Process**
1. **Fork** the project
2. **Create** your feature branch (`git checkout -b feature/amazing-feature`)
3. **Write** tests for your changes
4. **Run** the test suite (`make test-ci`)
5. **Commit** your changes (`git commit -m 'Add amazing feature'`)
6. **Push** to your branch (`git push origin feature/amazing-feature`)
7. **Open** a Pull Request

### **Development Standards**
- **Tests Required**: All new features must include tests
- **Documentation**: Update docstrings and README as needed
- **Code Quality**: Must pass `make test-ci` (formatting, linting, tests)
- **Type Hints**: All public APIs must include type annotations
- **Backward Compatibility**: No breaking changes without major version bump

### **Reporting Issues**
- **Bug Reports**: [GitHub Issues](https://github.com/ThaissaTeodoro/logging-metrics/issues)
- **Feature Requests**: Include use case and examples
- **Security Issues**: Email maintainer directly for sensitive issues

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](https://github.com/ThaissaTeodoro/LICENSE) file for details.

### **Quick Summary**
- ✅ **Commercial Use**: Can be used in commercial applications
- ✅ **Modification**: Can be modified and distributed
- ✅ **Distribution**: Can be distributed freely
- ✅ **Private Use**: Can be used privately
- ⚠️ **Liability**: No warranty provided
- 📋 **Attribution**: Must include original license

---

## 🌟 **Star History**

If this library helped you, please consider giving it a ⭐ on GitHub!

[![Star History](https://img.shields.io/github/stars/ThaissaTeodoro/logging-metrics?style=social)](https://github.com/ThaissaTeodoro/logging-metrics)

---

## 📞 **Support & Community**

- **📖 Documentation**: Complete examples in this README
- **🐛 Issues**: [GitHub Issues](https://github.com/ThaissaTeodoro/logging-metrics/issues)
- **🔄 Migration Help**: [Migration Guide](https://github.com/ThaissaTeodoro/logging-metrics/MIGRATION_GUIDE.md)
- **📧 Contact**: [thaissa.teodoro@hotmail.com](mailto:thaissa.teodoro@hotmail.com)

---

## 🚀 **Ready to Get Started?**

```bash
# Install the library
pip install logging-metrics

# Start with simple console logging
from logging_metrics import configure_basic_logging
logger = configure_basic_logging()
logger.info("Welcome to logging-metrics v1.0.0! 🎉")

# Or jump into production setup
from logging_metrics import setup_file_logging
logger = setup_file_logging("myapp", log_dir="./logs", json_format=True)
logger.info("Production logging ready!")
```

**Happy Logging!** 🎯

---

*Made with ❤️ for the Python community. Star ⭐ this repo if it helped you!*