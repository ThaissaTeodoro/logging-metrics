#!/usr/bin/env python3
"""
Script to run logging_toolkit tests with different configurations.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(cmd, description=""):
    """Executes a command and returns the exit code."""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"Running: {' '.join(cmd)}")
    print(f"{'='*60}")

    result = subprocess.run(cmd)
    return result.returncode

def setup_environment():
    """Set up the environment for testing."""
    current_dir = Path(__file__).parent.absolute()
    python_path = os.environ.get('PYTHONPATH', '')
    if str(current_dir) not in python_path.split(':'):
        os.environ['PYTHONPATH'] = f"{current_dir}:{python_path}".rstrip(':')

    os.environ.setdefault('PYSPARK_PYTHON', sys.executable)
    os.environ.setdefault('PYSPARK_DRIVER_PYTHON', sys.executable)

    print(f"Configured environment:")
    print(f"   - PYTHONPATH: {os.environ['PYTHONPATH']}")
    print(f"   - PYSPARK_PYTHON: {os.environ['PYSPARK_PYTHON']}")

def main():
    parser = argparse.ArgumentParser(description="Test runner for logging_toolkit")
    parser.add_argument('--coverage', action='store_true', help='Run tests with code coverage')
    parser.add_argument('--parallel', action='store_true', help='Run tests in parallel')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose mode')
    parser.add_argument('--markers', '-m', type=str, help='Only run tests with specific markers')
    parser.add_argument('--test-file', '-f', type=str, help='Run only a specific test file')
    parser.add_argument('--install-deps', action='store_true', help='Install dependencies before running tests')
    args = parser.parse_args()

    setup_environment()

    if args.install_deps:
        install_cmd = [sys.executable, '-m', 'pip', 'install', '-r', 'test-requirements.txt']
        if run_command(install_cmd, "Installing dependencies") != 0:
            print("Dependency installation failed")
            return 1

    pytest_cmd = [sys.executable, '-m', 'pytest']

    if args.coverage:
        pytest_cmd.extend([
            '--cov=logging',
            '--cov-report=html',
            '--cov-report=term-missing',
            '--cov-fail-under=80'
        ])

    if args.parallel:
        pytest_cmd.extend(['-n', 'auto'])  # pytest-xdist

    if args.verbose:
        pytest_cmd.append('-vv')

    if args.markers:
        pytest_cmd.extend(['-m', args.markers])

    if args.test_file:
        pytest_cmd.append(args.test_file)
    else:
        pytest_cmd.append('test_logging_toolkit.py')

    exit_code = run_command(pytest_cmd, "Executando testes")

    if exit_code == 0:
        print("\nTodos os testes passaram!!!")
        if args.coverage:
            print("📊 Relatório de cobertura gerado em htmlcov/index.html")
    else:
        print(f"\n❌ Testes falharam (código de saída: {exit_code})")

    return exit_code

if __name__ == "__main__":
    sys.exit(main())
