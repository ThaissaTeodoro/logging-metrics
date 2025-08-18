# Migration Guide - logging-metrics v1.0.0

## 🎉 **Great News: 100% Backward Compatible!**

If you're already using `logging-metrics`, your existing code will continue to work **exactly the same** without any changes required!

## 📊 **What's New in v1.0.0**

### 🏗️ **Modular Structure**
The library has been reorganized into specialized modules for better organization:

- **`logger.py`** - Logging functionality (formatters, handlers, configuration)
- **`timers.py`** - Timing utilities (`LogTimer`)  
- **`metrics.py`** - Metrics collection (`LogMetrics`)
- **`core.py`** - Backward compatibility (maintains all old imports)

### 🆕 **Enhanced Features**
- Formal public API with comprehensive documentation
- Robust error handling and input validation
- New LogMetrics methods for programmatic access
- Complete type hints for better IDE support
- Version information functions

---

## 🔄 **Migration Strategies**

### **Strategy 1: No Changes (Recommended for Existing Projects)**

Your existing code continues to work without any modifications:

```python
# ✅ This still works exactly as before
from logging_metrics import setup_file_logging, LogTimer, LogMetrics
from logging_metrics.core import configure_basic_logging

logger = setup_file_logging("myapp")
metrics = LogMetrics(logger)
```

### **Strategy 2: Gradual Migration (For New Features)**

Keep existing code unchanged, use modular imports for new functionality:

```python
# Existing code (unchanged)
from logging_metrics import setup_file_logging

# New features with modular imports
from logging_metrics.metrics import LogMetrics
from logging_metrics.timers import LogTimer

logger = setup_file_logging("myapp")
metrics = LogMetrics(logger)

# Use new v1.0.0 features
summary = metrics.get_summary()
has_counter = metrics.has_metric('requests')
```

### **Strategy 3: Full Migration (For New Projects)**

Use modular imports throughout for better organization:

```python
# Modern modular approach
from logging_metrics.logger import setup_file_logging, configure_basic_logging
from logging_metrics.timers import LogTimer
from logging_metrics.metrics import LogMetrics

logger = configure_basic_logging()
metrics = LogMetrics(logger)

with LogTimer(logger, "Operation"):
    # Your code here
    pass
```

---

## 🆕 **New Features Guide**

### **1. Enhanced LogMetrics**

```python
from logging_metrics.metrics import LogMetrics

metrics = LogMetrics(logger)

# NEW: Get current counter value
count = metrics.get_counter('requests')  # Returns 0 if doesn't exist

# NEW: Get value with default
status = metrics.get_value('status', 'unknown')

# NEW: Check if metric exists
if metrics.has_metric('response_time'):
    elapsed = metrics.get_timer_elapsed('response_time')

# NEW: List all metrics by type
all_metrics = metrics.list_metrics()
print(f"Available counters: {all_metrics['counters']}")

# NEW: Get comprehensive summary
summary = metrics.get_summary()
print(f"Total requests: {summary['counters'].get('requests', 0)}")

# NEW: Reset all metrics
metrics.reset()  # Clear everything for fresh start

# NEW: String representation
print(metrics)  # Shows counts and status
```

### **2. Enhanced LogTimer**

```python
from logging_metrics.timers import LogTimer

timer = LogTimer(logger, "Database query")

# NEW: Manual start/stop control
timer.start()
# ... perform operation ...
elapsed = timer.stop()

# NEW: Get current elapsed time (while running)
timer.start()
current_time = timer.elapsed()  # Get time without stopping

# NEW: String representation
print(timer)  # Shows operation name and status
```

### **3. Context Manager for Metrics Timing**

```python
# NEW: Automatic timing with context manager
with metrics.timer('database_operation'):
    result = database.query("SELECT * FROM users")
# Timer automatically started and stopped
```

### **4. Version Information**

```python
from logging_metrics import __version__, get_version, get_version_info

print(f"Version: {get_version()}")  # "1.0.0"
major, minor, patch = get_version_info()  # (1, 0, 0)
```

---

## 📚 **Import Options Comparison**

### **Traditional Imports (Still Work)**
```python
# Main package
from logging_metrics import (
    setup_file_logging,
    LogTimer, 
    LogMetrics,
    configure_basic_logging
)

# Core module (backward compatibility)
from logging_metrics.core import (
    ColoredFormatter,
    JSONFormatter,
    create_file_handler
)
```

### **Modern Modular Imports (Recommended for New Code)**
```python
# Specific functionality
from logging_metrics.logger import (
    setup_file_logging,
    configure_basic_logging,
    ColoredFormatter,
    JSONFormatter
)

from logging_metrics.timers import LogTimer
from logging_metrics.metrics import LogMetrics, TimerContext
```

---

## 🔧 **Configuration Updates**

### **Dependency Updates**

If you have `logging-metrics` in your `requirements.txt`:

```txt
# Before
logging-metrics

# After (recommended for stability)
logging-metrics>=1.0.0,<2.0.0
```

### **Type Checking Support**

v1.0.0 includes complete type hints:

```python
# mypy.ini or pyproject.toml
[tool.mypy]
# No special configuration needed - types are included!
```

---

## 🧪 **Testing Migration**

### **pytest Integration**

The caplog-friendly functionality is enhanced:

```python
# test_myapp.py
import pytest
from logging_metrics import get_logger

def test_my_function(caplog):
    logger = get_logger("test", caplog_friendly=True)
    
    # Your test code - works the same as before
    with caplog.at_level(logging.INFO):
        my_function(logger)
    
    assert "expected message" in caplog.text
```

---

## 🚨 **Troubleshooting**

### **Import Errors**

If you get import errors after upgrading:

```python
# ❌ Problem: Can't find specific functions
from logging_metrics.logger import LogTimer  # LogTimer is in timers!

# ✅ Solution: Check correct module
from logging_metrics.timers import LogTimer

# ✅ Alternative: Use compatibility imports
from logging_metrics.core import LogTimer  # Always works
```

### **Type Checking Issues**

If your type checker complains:

```python
# ✅ Use explicit imports for better type inference
from logging_metrics.logger import setup_file_logging
from logging_metrics.metrics import LogMetrics

# Instead of
from logging_metrics import *
```

### **Circular Import Issues**

If you experience circular imports:

```python
# ✅ Use the core module as fallback
from logging_metrics.core import setup_file_logging, LogTimer, LogMetrics
```

---

## 📋 **Migration Checklist**

### **Before Upgrading**
- [ ] Review your current imports
- [ ] Check if you're using any undocumented features
- [ ] Backup your current working version
- [ ] Run your existing tests

### **After Upgrading**
- [ ] Verify all imports still work
- [ ] Run your test suite
- [ ] Check logging output is as expected
- [ ] Consider using new features where beneficial
- [ ] Update documentation if you adopt modular imports

### **Optional Improvements**
- [ ] Switch to modular imports for new code
- [ ] Use new LogMetrics methods for better metrics access
- [ ] Add type hints if using TypeScript/mypy
- [ ] Update dependency version pinning

---

## 🎯 **Recommended Upgrade Path**

### **Step 1: Safe Upgrade**
1. Upgrade to v1.0.0
2. Run existing tests
3. Verify everything works

### **Step 2: Gradual Enhancement**
1. Use new LogMetrics methods where helpful
2. Adopt modular imports for new files
3. Add type hints gradually

### **Step 3: Full Modernization (Optional)**
1. Switch to modular imports throughout
2. Use new features consistently
3. Update documentation and examples

---

## ❓ **FAQ**

### **Q: Do I need to change my existing code?**
**A:** No! All existing code continues to work without changes.

### **Q: Should I switch to modular imports?**
**A:** It's optional. For new projects, modular imports provide better organization. For existing projects, you can keep current imports.

### **Q: Are there any breaking changes?**
**A:** No breaking changes. v1.0.0 is 100% backward compatible.

### **Q: What if I find a bug in v1.0.0?**
**A:** Report it on [GitHub Issues](https://github.com/ThaissaTeodoro/logging-metrics/issues). You can always downgrade to the previous version if needed.

### **Q: How do I know what's in the public API?**
**A:** Check the `__all__` exports in each module, or refer to the documentation. Anything not in `__all__` is considered internal.

---

## 📞 **Support**

- **Issues**: [GitHub Issues](https://github.com/ThaissaTeodoro/logging-metrics/issues)
- **Documentation**: [README.md](https://github.com/ThaissaTeodoro/logging-metrics/README.md)
- **Examples**: Check the examples in function docstrings

Remember: Migration is **optional**. Your code works as-is, and you can adopt new features at your own pace!