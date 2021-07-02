.PHONY: help dev build test cov style check clean docs autodocs all
.DEFAULT_GOAL := help
.SILENT:

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
	@echo " - check     :  Runs tests, coverage and style in sequence."
	@echo " - clean     :  Removes project clutter and cache files."
	@echo " - docs      :  Creates a clean docs build."
	@echo " - autodocs  :  Creates and serves a clean docs build."
	@echo " - all       :  Runs all of the above in an appropriate order (excluding 'dev', 'clean', and 'autodocs')."

.ONESHELL:
dev:
	@echo "\nCreating Development Environment\n"
	poetry install
	poetry run pre-commit install
	poetry run pre-commit autoupdate
	@echo "\nDon't forget to activate your virtual environment!"
	@echo "run: source .venv/bin/activate"

build:
	@echo "\nBuilding: pytoil\n"
	poetry build

test:
	@echo "\nRunning: pytest\n"
	poetry run pytest --cov=pytoil tests/

cov: test
	@echo "\nRunning: coverage\n"
	poetry run coverage report --show-missing
	poetry run coverage-badge -fo ./docs/img/coverage.svg

style:
	@echo "\nRunning: isort"
	poetry run isort .
	@echo "\nRunning: black"
	poetry run black .
	@echo "\nRunning: flake8"
	poetry run flake8 .
	@echo "\nRunning: mypy"
	poetry run mypy

check: cov style
	poetry run pre-commit run --all-files

clean:
	@echo "\nCleaning project clutter\n"
	find . -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache/ .nox/ .pytest_cache/ site/ .coverage *.egg-info

docs:
	@echo "\nBuilding Docs\n"
	poetry run mkdocs build --clean

autodocs:
	@echo "\nServing Docs\n"
	poetry run mkdocs serve

all: check docs
