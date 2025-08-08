import tempfile
import pytest
import shutil


@pytest.fixture
def tmp_log_dir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d)


# Mock logger
class MockLogger:
    """Mock logger for tests that don't need real logging."""

    def __init__(self):
        self.debug_calls, self.info_calls, self.warning_calls, self.error_calls = [], [], [], []

    def debug(self, msg):
        self.debug_calls.append(msg)

    def info(self, msg):
        self.info_calls.append(msg)

    def warning(self, msg):
        self.warning_calls.append(msg)

    def error(self, msg):
        self.error_calls.append(msg)


@pytest.fixture
def mock_logger():
    """Fixture that provides a mock logger."""
    return MockLogger()


# Clean SparkContext (enforces GC to not "leak" memory in many tests)
@pytest.fixture(autouse=True)
def cleanup_spark_context():
    yield
    import gc

    gc.collect()


def pytest_collection_modifyitems(config, items):
    """
    Automatically marks tests based on fixture usage or name..
    """
    for item in items:
        if "spark" in item.fixturenames:
            item.add_marker(pytest.mark.spark)
        if "Performance" in item.nodeid or "large" in item.name.lower():
            item.add_marker(pytest.mark.performance)
        if "Integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        if "Stress" in item.nodeid:
            item.add_marker(pytest.mark.stress)
        if "Test" in item.nodeid and all(
            x not in item.nodeid for x in ["Performance", "Integration", "Stress"]
        ):
            item.add_marker(pytest.mark.unit)
        if any(keyword in item.name.lower() for keyword in ["large", "performance", "slow"]):
            item.add_marker(pytest.mark.slow)
