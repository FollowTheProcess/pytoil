"""
Task configuration for 'doit' https://pydoit.org.

Effectively a python version of a makefile.
"""

import glob
import os
import shutil
import venv
from pathlib import Path

# Global project stuff
PROJECT_ROOT = Path(__file__).parent.resolve()
PROJECT_SRC = PROJECT_ROOT / "pytoil"
PROJECT_TESTS = PROJECT_ROOT / "tests"

# Global doit config
DOIT_CONFIG = {
    "backend": "sqlite3",
    "default_tasks": ["venv", "test", "lint", "docs"],
}

# Python virtual environment stuff
VENV_DIR = PROJECT_ROOT / ".venv"
PYTHON = os.fsdecode(VENV_DIR / "bin" / "python")

# Python file dependencies
PYTHON_FILES = glob.glob("**/*.py", recursive=True)
SETUP_CFG = PROJECT_ROOT / "setup.cfg"
PYPROJECT_TOML = PROJECT_ROOT / "pyproject.toml"

# Python build dependencies
BUILD_DIR = PROJECT_ROOT / "build"
DIST_DIR = PROJECT_ROOT / "dist"

# Docs file dependencies
DOCS_BUILD = PROJECT_ROOT / "site"
MARKDOWN_FILES = glob.glob("**/*.md", recursive=True)
MKDOCS_CONFIG = PROJECT_ROOT / "mkdocs.yml"

# Test stuff
COVERAGE_DATA = PROJECT_ROOT / ".coverage"


def task_venv():
    """
    Create a virtual environment & install dev dependencies.
    """

    return {
        "actions": [
            (venv.create, (VENV_DIR,), {"with_pip": True}),
            f"{PYTHON} -m pip install --quiet --upgrade pip setuptools wheel",
            f"{PYTHON} -m pip install --quiet -e .[dev]",
        ],
        "file_dep": [SETUP_CFG],
        "targets": [".venv"],
        "verbosity": 2,
        "clean": [(shutil.rmtree, (VENV_DIR,))],
    }


def task_build():
    """
    Builds the project's sdist and wheel.
    """

    def clean_up():
        """
        Helper to remove build targets.
        """
        shutil.rmtree(BUILD_DIR, ignore_errors=True)
        shutil.rmtree(DIST_DIR, ignore_errors=True)

    return {
        "actions": [f"{PYTHON} -m build --sdist --wheel"],
        "file_dep": PYTHON_FILES + [SETUP_CFG, PYPROJECT_TOML],
        "task_dep": ["venv"],
        "targets": [BUILD_DIR, DIST_DIR],
        "clean": [clean_up],
    }


def task_test():
    """
    Runs unit tests with pytest.
    """

    return {
        "actions": [f"{PYTHON} -m pytest --cov={PROJECT_SRC} {PROJECT_TESTS}/"],
        "file_dep": PYTHON_FILES,
        "task_dep": ["venv"],
        "verbosity": 2,
    }


def task_cov():
    """
    Shows coverage report.
    """

    def clean_up():
        """
        Helper to remove coverage data.
        """
        COVERAGE_DATA.unlink(missing_ok=True)

    return {
        "actions": [f"{PYTHON} -m coverage report --show-missing"],
        "file_dep": PYTHON_FILES,
        "task_dep": ["venv", "test"],
        "targets": [COVERAGE_DATA],
        "verbosity": 2,
        "clean": [clean_up],
    }


def lint_isort():
    """
    Sorts imports using isort.
    """

    return {
        "name": "isort",
        "actions": [f"{PYTHON} -m isort ."],
        "file_dep": PYTHON_FILES,
        "task_dep": ["venv"],
    }


def lint_black():
    """
    Formats code using black.
    """

    return {
        "name": "black",
        "actions": [f"{PYTHON} -m black ."],
        "file_dep": PYTHON_FILES,
        "task_dep": ["venv"],
    }


def lint_flake8():
    """
    Lints code using flake8.
    """

    return {
        "name": "flake8",
        "actions": [f"{PYTHON} -m flake8 ."],
        "file_dep": PYTHON_FILES,
        "task_dep": ["venv"],
    }


def lint_mypy():
    """
    Type checks code using mypy.
    """

    return {
        "name": "mypy",
        "actions": [f"{PYTHON} -m mypy ."],
        "file_dep": PYTHON_FILES,
        "task_dep": ["venv"],
    }


def task_lint():
    """
    Runs all linting, type checking & formatting.
    """

    yield lint_isort()
    yield lint_black()
    yield lint_flake8()
    yield lint_mypy()


def task_docs():
    """
    Builds docs using mkdocs.
    """

    return {
        "actions": [f"{PYTHON} -m mkdocs build --clean"],
        "file_dep": MARKDOWN_FILES,
        "task_dep": ["venv"],
        "targets": [DOCS_BUILD],
        "clean": [(shutil.rmtree, (DOCS_BUILD,))],
    }
