# Test Guide - logging_toolkit

This guide explains how to run, configure, and interpret automated tests for the `logging_toolkit` library.

## 📁 File Structure

```
logging_toolkit/
├── logging_toolkit.py                  # Main library
├── test_logging_toolkit.py             # Unit & integration tests (functions, classes, edge cases)
├── test_logging_toolkit_performance.py # Performance/massive logs tests (optional)
├── conftest.py                         # Pytest configuration (fixtures, loggers, env)
├── pytest.ini                          # Pytest config (markers, logs, warnings)
├── test-requirements.txt               # Test dependencies
├── run_tests.py                        # Python script for test execution
├── Makefile                            # Automated commands (lint, test, coverage, etc.)
└── TEST_GUIDE.md                       # (This file)
```

## 🚀 Quick Start

### Option 1: Using Makefile (Recommended)
```bash
make install         # Install dependencies
make test            # Run all tests
make test-cov        # Run tests with code coverage
make test-parallel   # Run tests in parallel
```

### Option 2: Using the Python Script
```bash
# Install dependencies and run tests with coverage
python run_tests.py --install-deps --coverage

# Run only fast tests
python run_tests.py --markers "not slow"
```

### Option 3: Using pytest Directly
```bash
# Install dependencies
pip install -r test-requirements.txt

# Run basic tests
pytest test_logging_toolkit.py -v

# Run with coverage
pytest test_logging_toolkit.py --cov=logging_toolkit --cov-report=html -v
```

## 📊 Types of Tests

### 1. Unit Tests
Test individual functions and classes in isolation:
```bash
# Run only unit tests
make test-unit
# or
pytest -m "unit" -v
```
**Coverage includes:**
- ✅ Formatters (ColoredFormatter, JSONFormatter)
- ✅ Handlers (file, console, rotation)
- ✅ get_logger, configure_basic_logging
- ✅ LogTimer, LogMetrics
- ✅ DataFrame logging (with mocks)

### 2. Integration Tests
End-to-end flows: logging configuration + real instrumentation.
```bash
# Run only integration tests
make test-integration
# or
pytest -m "integration" -v
```
**Examples:**
- Log rotation by time/size
- Simultaneous logging to console and file
- Instrumentation of real functions and DataFrames

## 🏷️ Markers

Tests use markers for categorization:

| Marker       | Description                        | Example Usage         |
|--------------|------------------------------------|----------------------|
| `unit`       | Unit tests                         | `pytest -m unit`     |
| `integration`| Integration tests                  | `pytest -m integration`|
| `slow`       | Long-running tests (>5s)           | `pytest -m "not slow"`|
| `spark`      | Tests involving PySpark            | `pytest -m spark`    |

## 📈 Coverage Reports

### View HTML Coverage
```bash
make test-cov
# Open htmlcov/index.html in your browser
```

### Coverage Targets
- **Current goal:** 90%+
- **Minimum acceptable:** 80%
- **Files covered:** `logging_toolkit.py`

## 🔧 Specific Test Scenarios

### Edge Case Tests
```bash
# Test behavior with problematic data
pytest test_logging_toolkit.py::TestEdgeCases -v
```
**Cases covered:**
- Loggers without handlers
- Duplicate loggers
- LogTimer/LogMetrics raising exceptions
- Logging in terminal-less environments (CI)

### Formatter Tests
```bash
# Test type conversions and formatting
pytest test_logging_toolkit.py::TestFormatters -v
```
**Types checked:**
- Colored output, JSON, plain text
- Chained handlers

### PySpark Instrumentation
```bash
pytest -m spark
```
**Scalability scenarios:**
- DataFrame logging (log_spark_dataframe_info)
- Log capture in simulated Spark jobs (with mocks)

## 📊 Interpreting Results

### Normal Successful Output
```
======================== test session starts ========================
test_logging_toolkit.py::TestLogTimer PASSED [10%]
test_logging_toolkit.py::TestLogMetrics PASSED [20%]
...
======================== 48 passed in 12.34s ========================
```

### Common Failures/Troubleshooting
- Logs not showing in caplog: Use `get_logger(..., propagate=True)` in the test!
- Duplicate handlers: Ensure you don't add a new handler for each test.
- Race condition: File handlers blocking on slow systems?
- Use temp directories or adjust rotation settings.

## 🐛 Debugging & Troubleshooting

### Run in Debug Mode
```bash
# Debug with breakpoints
make test-debug
# or
pytest --pdb -v

# Debug a specific test
pytest --log-cli-level=DEBUG --capture=no -v
```
#### Tips
- If logs aren’t captured, check `propagate` and handlers.
- Use `caplog.records` (not `capsys`) for log assertions.
- For visual debugging, run a test and inspect output files in temp folders.

## Checklist for New Tests
- Descriptive name (test_function_scenario)
- Docstring explaining the test
- Mock logging objects if needed
- Check output in `caplog.records` (not stdout)
- Edge cases: logger without handler, duplicate log, root logger
- Test colored, JSON, and rotating formats
- Test LogTimer as context manager and decorator
- Test LogMetrics with various metric types
- Acceptable performance (massive logs < 30s)

## Continuous Execution & Development

### Watch Mode
```bash
make test-watch
pytest --looponfail
```
### Specific Tests
```bash
pytest -k "LogTimer" -v
pytest test_logging_toolkit.py::TestLogTimer::test_context_and_decorator -v
```

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
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Run tests
        run: make test-ci
```

### Full Pipeline
```bash
make quality-check  # Lint + format + test + coverage
```

### Example Test Snippets
```python
def test_configure_basic_logging_and_get_logger(caplog):
    configure_basic_logging(level=logging.DEBUG, use_colors=False)
    logger = get_logger("my.logger", level=logging.DEBUG, propagate=True)
    with caplog.at_level(logging.DEBUG):
        logger.info("info message")
        logger.error("error message")
    msgs = " ".join(r.getMessage() for r in caplog.records)
    assert "info message" in msgs
    assert "error message" in msgs

def test_logtimer_context_and_decorator(caplog):
    logger = get_logger("timer", propagate=True)
    with LogTimer(logger, "Context Operation"):
        time.sleep(0.05)
    assert any("Completed: Context Operation" in r.getMessage() for r in caplog.records)
```
---

## 🎯 Main Command Summary

| Action         | Command             |
|----------------|--------------------|
| **Setup**      | `make install`     |
| **Basic tests**| `make test`        |
| **With coverage** | `make test-cov` |
| **Linting**    | `make lint`        |
| **Debug**      | `make test-debug`  |
| **Clean**      | `make clean`       |
| **Pipeline**   | `make quality-check`|
