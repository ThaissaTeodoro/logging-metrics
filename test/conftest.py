"""
Configurações compartilhadas para todos os testes do logging_toolkit.
"""

import tempfile
import pytest
import shutil
from pyspark.sql import Row
import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType

# Fixtures para DataFrames de uso recorrente nos testes
@pytest.fixture
def tmp_log_dir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d)

# Mock logger
class MockLogger:
    """Logger simulado para testes que não precisam de logging real."""
    def __init__(self):
        self.debug_calls, self.info_calls, self.warning_calls, self.error_calls = [], [], [], []
    def debug(self, msg): self.debug_calls.append(msg)
    def info(self, msg): self.info_calls.append(msg)
    def warning(self, msg): self.warning_calls.append(msg)
    def error(self, msg): self.error_calls.append(msg)

@pytest.fixture
def mock_logger():
    """Fixture que fornece um mock logger."""
    return MockLogger()

# Limpa SparkContext (reforça GC para não "vazar" memória em muitos testes)
@pytest.fixture(autouse=True)
def cleanup_spark_context():
    yield
    import gc
    gc.collect()

# Configurações para ambientes de teste/CI
@pytest.fixture(scope="session", autouse=True)
def configure_test_environment():
    os.environ["SPARK_LOCAL_IP"] = "127.0.0.1"
    os.environ["SPARK_DRIVER_MEMORY"] = "1g"
    os.environ["SPARK_EXECUTOR_MEMORY"] = "1g"
    yield

def pytest_collection_modifyitems(config, items):
    """
    Marca testes automaticamente conforme uso de fixtures ou nome.
    """
    for item in items:
        # Marca testes que usam SparkSession
        if "spark" in item.fixturenames:
            item.add_marker(pytest.mark.spark)
        # Marca performance, integração ou stress por nome ou classe
        if "Performance" in item.nodeid or "large" in item.name.lower():
            item.add_marker(pytest.mark.performance)
        if "Integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        if "Stress" in item.nodeid:
            item.add_marker(pytest.mark.stress)
        # Marca unit por padrão
        if "Test" in item.nodeid and all(x not in item.nodeid for x in ["Performance", "Integration", "Stress"]):
            item.add_marker(pytest.mark.unit)
        # Marca slow se nome indicar
        if any(keyword in item.name.lower() for keyword in ["large", "performance", "slow"]):
            item.add_marker(pytest.mark.slow)
