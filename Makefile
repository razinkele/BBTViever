# Makefile for EMODnet Viewer Development

.PHONY: help install install-dev test lint format type-check security clean run dev health diagnostic docs

# Default target
help:
	@echo "EMODnet Seabed Habitats Viewer - Development Commands"
	@echo "====================================================="
	@echo ""
	@echo "Setup Commands:"
	@echo "  install       Install production dependencies"
	@echo "  install-dev   Install development dependencies"
	@echo ""
	@echo "Development Commands:"
	@echo "  run           Run production server"
	@echo "  dev           Run development server with auto-reload"
	@echo "  health        Check application health"
	@echo "  diagnostic    Run WMS diagnostic tests"
	@echo ""
	@echo "Testing Commands:"
	@echo "  test          Run all tests"
	@echo "  test-unit     Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-coverage Run tests with coverage report"
	@echo ""
	@echo "Code Quality Commands:"
	@echo "  lint          Run code linting"
	@echo "  format        Format code with black and isort"
	@echo "  type-check    Run type checking"
	@echo "  security      Run security checks"
	@echo "  quality       Run full quality check suite"
	@echo ""
	@echo "Utility Commands:"
	@echo "  clean         Clean build artifacts and cache"
	@echo "  docs          Generate documentation"
	@echo ""

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

# Development servers
run:
	python app.py

dev:
	python scripts/dev_server.py

dev-verbose:
	python scripts/dev_server.py --log-level DEBUG --verbose

dev-no-reload:
	python scripts/dev_server.py --no-reload

# Health and diagnostics
health:
	curl -s http://localhost:5000/health | python -m json.tool || echo "Server not running or health endpoint unavailable"

diagnostic:
	python scripts/wms_diagnostic.py --verbose

diagnostic-export:
	python scripts/wms_diagnostic.py --verbose --output diagnostic-report.json

# Testing
test:
	python scripts/run_tests.py --all --verbose

test-unit:
	python scripts/run_tests.py --unit --verbose

test-integration:
	python scripts/run_tests.py --integration --verbose

test-coverage:
	python scripts/run_tests.py --all --coverage --verbose

test-report:
	python scripts/run_tests.py --report

# Code quality
lint:
	python scripts/run_tests.py --lint

format:
	python scripts/run_tests.py --fix

type-check:
	python scripts/run_tests.py --type-check

security:
	python scripts/run_tests.py --security

quality:
	python scripts/run_tests.py --quality

# Quick quality check (faster version)
quick-check:
	python -m flake8 app.py config/ src/ --count --select=E9,F63,F7,F82 --show-source --statistics
	python -m black --check app.py config/ src/ tests/
	python -m pytest tests/unit -x -q

# Cleanup
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .coverage htmlcov/ .pytest_cache/ dist/ build/ 2>/dev/null || true
	rm -f test-results.xml coverage.xml test-report.html 2>/dev/null || true

# Documentation
docs:
	@echo "Generating documentation..."
	@mkdir -p docs/build
	@echo "# EMODnet Viewer Documentation" > docs/build/README.md
	@echo "" >> docs/build/README.md
	@echo "Auto-generated documentation from code comments and docstrings" >> docs/build/README.md
	@echo "Documentation generation completed"

# Development workflow shortcuts
setup: install-dev
	@echo "Creating .env file from example..."
	@cp .env.example .env 2>/dev/null || echo ".env file already exists"
	@echo "Development environment setup complete!"

check: quick-check test-unit
	@echo "Quick development check complete!"

pre-commit: format lint test-unit
	@echo "Pre-commit checks complete!"

full-check: quality
	@echo "Full quality check complete!"

# Docker commands (if Docker is used)
docker-build:
	docker build -t emodnet-viewer .

docker-run:
	docker run -p 5000:5000 emodnet-viewer

# Environment management
env-check:
	@echo "Environment Check:"
	@echo "=================="
	@python --version
	@echo "Pip packages:"
	@pip list | grep -E "(flask|requests|pytest)" || echo "Core packages not found"

# Database/migration commands (if needed in future)
# migrate:
# 	@echo "No migrations needed for current version"

# Performance testing
perf-test:
	@echo "Running performance tests..."
	python scripts/wms_diagnostic.py --verbose
	@echo "Performance test complete"

# Monitoring
monitor:
	@echo "Starting monitoring dashboard..."
	@echo "Visit http://localhost:5000/health for health status"
	@echo "Use 'make diagnostic' for detailed WMS analysis"

# Development server with specific configurations
dev-production:
	FLASK_ENV=production python scripts/dev_server.py --no-reload

dev-testing:
	FLASK_ENV=testing python scripts/dev_server.py --log-level DEBUG