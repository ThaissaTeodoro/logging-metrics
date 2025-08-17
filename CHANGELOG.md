# Changelog - logging-metrics

All significant changes to this project will be documented in this file.

The format follows the guidelines from [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2025-08-16

### 🎉 **MAJOR RELEASE - PRODUCTION READY**

This release marks the first stable version of logging-metrics with a formal public API,
comprehensive error handling, and production-ready features.

### ✨ **Added**
- **Formal Public API**: Defined `__all__` exports in all modules for clear API boundaries
- **Comprehensive Documentation**: Google-style docstrings for all public functions and classes
- **Robust Error Handling**: Input validation and meaningful error messages throughout
- **Version Information**: `__version__`, `__version_info__`, `get_version()`, `get_version_info()`
- **Enhanced LogMetrics**: New methods for programmatic access to metrics data
  - `get_counter()` - Get current counter value
  - `get_value()` - Get current value with default
  - `get_timer_elapsed()` - Get timer elapsed time
  - `has_metric()` - Check if metric exists
  - `list_metrics()` - List all metric names by type
  - `__repr__()` - String representation of metrics state
- **Enhanced LogTimer**: Additional functionality and error handling
  - `start()` / `stop()` methods for manual control
  - `elapsed()` method for current elapsed time
  - `__repr__()` - String representation of timer state
  - Better exception handling in context manager
- **Type Hints**: Complete type annotations for all public APIs
- **Timezone Validation**: Robust timezone handling with fallback mechanisms
- **Path Handling**: Using `pathlib.Path` for better cross-platform compatibility
- **Comprehensive Test Suite**: 85%+ coverage with edge cases and error conditions

### 🏗️ **Modular Structure (Maintained)**
- **Complete Backward Compatibility**: All existing code continues to work
- **`logger.py`**: Core logging functionality (formatters, handlers, configuration)
- **`timers.py`**: Timing utilities (`LogTimer`)
- **`metrics.py`**: Metrics collection (`LogMetrics`, `TimerContext`)  
- **`core.py`**: Backward compatibility module (imports from new structure)

### 🔧 **Improved**
- **Error Messages**: More descriptive and actionable error messages
- **Input Validation**: Comprehensive validation of all function parameters
- **Resource Management**: Better cleanup and resource handling
- **Performance**: Optimized string operations and reduced overhead
- **JSON Serialization**: Improved handling of non-serializable objects
- **File Operations**: Better permission checking and error recovery
- **Spark Integration**: Enhanced error handling for DataFrame operations

### 🛡️ **Security & Robustness**
- **Input Sanitization**: Validation of all user inputs
- **Resource Limits**: Protection against excessive resource usage  
- **Exception Safety**: Proper cleanup even when exceptions occur
- **Permission Checking**: Validation of file system permissions before operations

### 📚 **Documentation**
- **API Reference**: Complete documentation for all public functions
- **Examples**: Comprehensive usage examples in docstrings
- **Error Handling**: Documented exceptions and error conditions
- **Type Information**: Full type hints for better IDE support

### 🧪 **Testing**
- **Unit Tests**: Complete coverage of all public APIs
- **Integration Tests**: End-to-end workflow testing
- **Error Testing**: Validation of error handling and edge cases
- **Performance Tests**: Timing and overhead validation
- **Spark Tests**: PySpark integration testing (when available)

### 📦 **Dependencies**
- **Pinned Versions**: Specific version ranges for stability
  - `pytz>=2023.3,<2025.0` (was: `pytz`)
- **Optional Dependencies**: Cleaner separation of optional features
  - `spark` extra: PySpark integration
  - `dev` extra: Development and testing tools

### 🔄 **Migration from 0.x.x**
- **No Breaking Changes**: 100% backward compatibility maintained
- **New Import Options**: Can use modular imports for better organization
- **Enhanced Functionality**: Existing code gets new features automatically

### ⚙️ **Internal Changes**
- **Code Quality**: Improved code organization and maintainability
- **Error Handling**: Consistent error handling patterns throughout
- **Resource Management**: Better cleanup and resource disposal
- **Performance**: Reduced overhead and improved efficiency

---

## [0.2.3] - 2025-08-09

### Added
- Unit and integration tests
- Improved examples in README
- Parameters to control computational cost in Spark operations

### Fixed
- File rotation bug on Windows
- Various minor bug fixes

---

## [0.1.2] - 2025-08-06

### Added
- Adjustments in README
- New development dependencies

---

## [0.1.1] - 2025-08-06

### Added
- Adjustments in README  
- New development dependencies

---

## [0.1.0] - 2025-08-05

### Added
- **Initial Release**: First version of logging-metrics library
- **Core Logging**: Colored logs for console output
- **File Rotation**: Support for time-based and size-based log rotation
- **PySpark Integration**: DataFrame logging capabilities
- **JSON Formatting**: Structured logging for external tools
- **LogTimer**: Context manager and decorator for execution timing
- **LogMetrics**: Basic metrics collection and logging
- **Basic Documentation**: Installation and usage examples

### Features
- Colored console output with customizable formatters
- Automatic log file rotation (time and size-based)
- Integration with PySpark DataFrames
- JSON output for log analysis tools
- Context managers for operation timing
- Basic metrics collection system

---

## Migration Guide

### From 0.x.x to 1.0.0

**✅ No Code Changes Required**: Your existing code will continue to work exactly as before.

**🆕 Optional Enhancements**: You can optionally take advantage of new features:

```python
# Your existing code (still works):
from logging_metrics import setup_file_logging, LogTimer, LogMetrics

# New modular imports (optional):
from logging_metrics.logger import setup_file_logging
from logging_metrics.timers import LogTimer
from logging_metrics.metrics import LogMetrics

# New LogMetrics features:
metrics = LogMetrics(logger)
summary = metrics.get_summary()  # Get programmatic access
metrics.reset()  # Clear all metrics
if metrics.has_metric('counter_name'):  # Check existence
    count = metrics.get_counter('counter_name')  # Get current value
```

For detailed migration information, see [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md).

---

## Support

- **Issues**: [GitHub Issues](https://github.com/ThaissaTeodoro/logging-metrics/issues)
- **Documentation**: [README.md](README.md)
- **Migration Help**: [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)