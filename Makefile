.PHONY: help install test test-cov test-parallel test-unit test-integration clean lint format quality-check

PYTHON := python3
PIP := $(PYTHON) -m pip
PYTEST := $(PYTHON) -m pytest

PKG := logging_metrics    
TESTS := test              


RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m 

help:
	@echo "$(BLUE)Targets: install, test, test-cov, test-parallel, test-unit, test-integration, lint, format, clean"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

install:
	@echo "$(YELLOW)Installing dependencies...$(NC)"
	$(PIP) install -U pip
	$(PIP) install -r $(TESTS)test-requirements.txt
	$(PIP) install -e .

test: 
	@echo "$(BLUE)Running all tests...$(NC)"
	$(PYTEST) $(TESTS) -v

test-cov:
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	$(PYTEST) $(TESTS) -v --cov=$(PKG) --cov-report=xml --cov-report=html --cov-report=term-missing
	@echo "$(GREEN)Coverage report available at htmlcov/index.html$(NC)"

test-parallel:
	@echo "$(BLUE)Running tests in parallel...$(NC)"
	$(PYTEST) $(TESTS) -n auto -v --cov=$(PKG) --cov-report=term-missing

test-unit:
	@echo "$(BLUE)Running unit tests...$(NC)"
	$(PYTEST) $(TESTS) -m "not integration" -v

test-integration:
	@echo "$(BLUE)Running integration tests...$(NC)"
	$(PYTEST) $(TESTS) -m integration -v

test-fast:
	@echo "$(BLUE)Running quick tests...$(NC)"
	$(PYTEST) $(TESTS) -m "not slow" -v

test-watch:
	@echo "$(BLUE)Watch mode enabled - tests will run when files change$(NC)"
	$(PYTEST) $(TESTS) --looponfail

test-debug:
	@echo "$(BLUE)Running tests in debug mode...$(NC)"
	$(PYTEST) $(TESTS) --pdb -v

test-profile:
	@echo "$(BLUE)Running tests with profiling...$(NC)"
	$(PYTEST) $(TESTS) --profile -v

test-report:
	@echo "$(BLUE)Generating test report...$(NC)"
	$(PYTEST) $(TESTS) --html=report.html --self-contained-html -v
	@echo "$(GREEN)Report available at report.html$(NC)"

test-local: 
	clean install test-cov 
	@echo "$(GREEN)Local setup completed successfully!$(NC)"

test-ci: 
	clean install quality-check
	@echo "$(GREEN)CI/CD pipeline completed!$(NC)"

quality-check: 
	lint test-cov
	@echo "$(GREEN)Quality check completed!$(NC)"

lint: 
	@echo "$(YELLOW)Performing linting...$(NC)"
	flake8 src/$(PKG) $(TESTS) --max-line-length=100 --ignore=E203,W503

format: 
	@echo "$(YELLOW)Format code...$(NC)"
	black src/$(PKG) $(TESTS) --line-length=100

quality-check: format test-cov

clean:
	@echo "$(YELLOW)Cleaning up temporary files...$(NC)"
	rm -rf .pytest_cache htmlcov .coverage coverage.xml __pycache__ */__pycache__ *.pyc

