# Test Guide - logging_toolkit

This guide explains how to run, configure, and interpret automated tests for the `logging_toolkit` library.

---

## 📁 File Structure

```
logging_toolkit/
├── logging_toolkit.py          # Main library
├── test_logging_toolkit.py     # Unit & integration tests (functions, classes, edge cases)
├── conftest.py                 # Pytest configuration (fixtures, temp dirs, mocks)
├── pytest.ini                  # Pytest config (markers, logs, warnings)
├── test-requirements.txt       # Test dependencies
├── Makefile                    # Automated commands (lint, test, coverage, etc.)
└── TEST_GUIDE.md               # (This file)
```

---

## 🚀 Quick Start

### Option 1: Using Makefile (Recommended)
```bash
make install         # Install dependencies
make test            # Run all tests
make test-cov        # Run tests with coverage report
make test-parallel   # Run tests in parallel
```

### Option 2: Using pytest directly
```bash
# Install dependencies
pip install -r test-requirements.txt

# Run basic tests
pytest test_logging_toolkit.py -v

# Run with coverage
pytest test_logging_toolkit.py --cov=logging_toolkit --cov-report=html -v
```

---

## 📊 Types of Tests

### 1. Unit Tests
Isolated tests for each function and class:
```bash
pytest -m "unit" -v
```
**Coverage includes:**
- ✅ `ColoredFormatter` (with and without colors)
- ✅ `JSONFormatter` (normal and with exceptions)
- ✅ File and timed rotation handlers
- ✅ Console handler creation
- ✅ `configure_basic_logging` + `get_logger` variations
- ✅ `LogTimer` as context manager and decorator
- ✅ `LogMetrics` (increment, set, timers, log_all)
- ✅ `_make_timezone_converter`

---

### 2. Integration Tests
End-to-end flows using multiple components together:
```bash
pytest -m "integration" -v
```
**Examples:**
- File + console logging with JSON output
- Log rotation by size and time
- Spark DataFrame logging (`log_spark_dataframe_info`)
- Custom handler injection into `get_logger`

---

### 3. Spark Tests
Tests that require PySpark:
```bash
pytest -m spark
```
- Logging schema, sample, and stats from Spark DataFrames
- Handling `None` DataFrame input gracefully

---

## 🏷️ Markers

| Marker       | Description                         |
|--------------|-------------------------------------|
| `unit`       | Unit tests                          |
| `integration`| Integration tests                   |
| `spark`      | Tests involving PySpark             |
| `slow`       | Long-running tests (>5s)            |

---

## 📈 Coverage Reports

### View HTML Coverage
```bash
make test-cov
# Open htmlcov/index.html in your browser
```

### Coverage Targets
- **Current goal:** 90%+
- **Minimum acceptable:** 85%
- **Files covered:** `logging_toolkit.py`

---

## 🔧 Specific Test Scenarios

### Formatter Tests
```bash
pytest test_logging_toolkit.py::test_colored_formatter_colors -v
pytest test_logging_toolkit.py::test_json_formatter_exception -v
```
**Covers:**
- ANSI color codes in logs
- JSON structure validation
- Exception serialization in JSON

---

### File Rotation Tests
```bash
pytest test_logging_toolkit.py::test_create_file_handler_and_rotation -v
pytest test_logging_toolkit.py::test_create_timed_file_handler -v
```
**Covers:**
- Size-based rotation
- Time-based rotation
- Backup file creation

---

### Timer & Metrics
```bash
pytest test_logging_toolkit.py::test_logtimer_context_and_decorator -v
pytest test_logging_toolkit.py::test_logmetrics_increment_set_log_logall -v
```
**Covers:**
- Timing with context manager and decorator
- Incrementing, setting, timing, and logging metrics

---

### Spark DataFrame Logging
```bash
pytest test_logging_toolkit.py::test_log_spark_dataframe_info_basic -v
pytest test_logging_toolkit.py::test_log_spark_dataframe_info_none -v
```
**Covers:**
- Schema, sample, and stats logging for DataFrames
- Handling `None` DataFrame input

---

## 📊 Interpreting Results

### Successful Run
```
======================== test session starts ========================
test_logging_toolkit.py::test_colored_formatter_colors PASSED  [ 10%]
test_logging_toolkit.py::test_json_formatter_simple PASSED     [ 20%]
...
======================== 22 passed in 3.45s ========================
```

### Common Failures
- **PySpark not installed** → Spark tests will be skipped (`pytest.mark.skipif`).
- **File permission issues** → Check temp directory permissions for rotation tests.
- **Handler duplication** → Clear handlers before adding new ones in setup.

---

## 🐛 Debugging & Troubleshooting

### Run in Debug Mode
```bash
make test-debug
# or
pytest --pdb -v
```

### Debug specific test
```bash
pytest -k "LogTimer" -v
pytest test_logging_toolkit.py::test_logtimer_context_and_decorator -v
```

---

## ✅ Checklist for New Tests
- Descriptive name (`test_function_scenario`)
- Docstring explaining the test
- Use pytest fixtures (`caplog`, `capsys`, `tmp_path`) when possible
- Test both normal and edge cases
- Include logging with/without colors, JSON, and rotation
- For Spark, handle both DataFrame and `None`

---

## 🚀 CI/CD Integration

### GitHub Actions Example
```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Run tests
        run: make test-ci
```

**Full Pipeline:**
```bash
make quality-check  # Lint + format + test + coverage
```
