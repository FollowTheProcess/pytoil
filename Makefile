.PHONY: docs
.DEFAULT_GOAL := help

help:
	@echo "Use 'make' when you just want to run a quick task. You'll need to run 'make dev' to install all dev dependencies.\n"
	@echo "Ensure you have created and activated your virtual environment before using any of these commands.\n"
	@echo "Available Commands:\n"
	@echo " - help      :  Show this help message."
	@echo " - dev       :  Installs project including development dependencies in editable mode."
	@echo " - test      :  Runs all unit tests."
	@echo " - cov       :  Shows test coverage."
	@echo " - style     :  Lints and style checks the entire project (isort, black, flake8 and mypy)."
	@echo " - check     :  Runs tests, coverage and style in sequence."
	@echo " - clean     :  Removes project clutter and cache files."
	@echo " - docs      :  Creates a clean docs build."
	@echo " - autodocs  :  Creates and serves a clean docs build."
	@echo " - all       :  Runs all of the above in an appropriate order (excluding 'dev', 'clean', and 'autodocs')."

dev:
	poetry install

test:
	pytest --cov=pytoil tests/

cov: test
	coverage report --show-missing
	coverage-badge -fo ./docs/img/coverage.svg

style:
	isort .
	black .
	flake8 .
	mypy .

check: cov style

clean:
	# Requires fd: brew install fd
	fd --no-ignore __pycache__ --exec rm -rf
	rm -rf .mypy_cache/ .nox/ .pytest_cache/ site/ .coverage

docs:
	mkdocs build --clean

autodocs:
	mkdocs serve

all: check docs