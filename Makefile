.PHONY: help dev build test cov style check clean docs autodocs all
.DEFAULT_GOAL := help
.SILENT:
.ONESHELL:

help:
	@echo "\nUse 'make' when you just want to run a quick task. You'll need to run 'make dev' to install all dev dependencies.\n"
	@echo "Ensure you have created and activated your virtual environment before using any of these commands.\n"
	@echo "Available Commands:\n"
	@echo " - help      :  Show this help message."
	@echo " - dev       :  Installs project including development dependencies in editable mode."
	@echo " - build     :  Builds the source distribution and wheel."
	@echo " - test      :  Runs all unit tests."
	@echo " - cov       :  Shows test coverage."
	@echo " - style     :  Lints and style checks the entire project (isort, black, flake8 and mypy)."
	@echo " - check     :  Runs tests, coverage, style and all pre-commit hooks in sequence."
	@echo " - clean     :  Removes project clutter and cache files."
	@echo " - docs      :  Creates a clean docs build."
	@echo " - autodocs  :  Creates and serves a clean docs build."
	@echo " - all       :  Runs all of the above in an appropriate order (excluding 'dev', 'clean', and 'autodocs')."

dev:
	@echo "\nCreating Development Environment\n"
	if [ ! -d ".venv" ]; then \
		python3 -m venv .venv; \
	fi
	source .venv/bin/activate
	python3 -m pip install --upgrade pip setuptools wheel
	python3 -m pip install -e .[dev]
	pre-commit install
	pre-commit autoupdate

build:
	@echo "\nBuilding: pytoil\n"
	python3 -m build --sdist --wheel

test:
	@echo "\nRunning: pytest\n"
	pytest --cov=pytoil tests/

cov: test
	@echo "\nRunning: coverage\n"
	coverage report --show-missing
	coverage-badge -fo ./docs/img/coverage.svg

style:
	@echo "\nRunning: isort"
	isort .
	@echo "\nRunning: black"
	black .
	@echo "\nRunning: flake8"
	flake8 .
	@echo "\nRunning: mypy"
	mypy .

check: cov style
	pre-commit run --all-files

clean:
	@echo "\nCleaning project clutter\n"
	find . -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache/ .nox/ .pytest_cache/ site/ .coverage *.egg-info build/ dist/

docs:
	@echo "\nBuilding Docs\n"
	mkdocs build --clean

autodocs:
	@echo "\nServing Docs\n"
	mkdocs serve

all: check docs
