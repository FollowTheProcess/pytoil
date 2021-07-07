"""
Task configuration for 'doit' https://pydoit.org.

Effectively a python version of a makefile.
"""

import glob
import json
import os
import shutil
from pathlib import Path

# Global project stuff
PROJECT_ROOT = Path(__file__).parent.resolve()
PROJECT_SRC = PROJECT_ROOT / "pytoil"
PROJECT_TESTS = PROJECT_ROOT / "tests"

# VSCode
VSCODE_DIR = PROJECT_ROOT / ".vscode"
SETTINGS_JSON = VSCODE_DIR / "settings.json"

# Global doit config
DOIT_CONFIG = {
    "minversion": "0.33.1",
    "backend": "sqlite3",
    "action_string_formatting": "new",
    "cleandeps": True,
    "cleanforget": True,
    "default_tasks": ["dev", "test", "lint", "cov", "docs"],
}

# Poetry virtual environment stuff
VENV_DIR = PROJECT_ROOT / ".venv"
PYTHON = os.fsdecode(VENV_DIR / "bin" / "python")
POETRY_LOCK = PROJECT_ROOT / "poetry.lock"

# Python file dependencies
PYTHON_FILES = glob.glob("**/*.py", recursive=True)
PYPROJECT_TOML = PROJECT_ROOT / "pyproject.toml"

# Poetry build dependencies
DIST_DIR = PROJECT_ROOT / "dist"

# Docs file dependencies
DOCS_BUILD = PROJECT_ROOT / "site"
MARKDOWN_FILES = glob.glob("**/*.md", recursive=True)
MKDOCS_CONFIG = PROJECT_ROOT / "mkdocs.yml"

# Test stuff
COVERAGE_DATA = PROJECT_ROOT / ".coverage"


def set_up_vscode() -> None:
    """
    Helper function that will set VSCode's workspace settings
    to use the auto-created virtual environment and enable
    pytest support.
    """

    if not VSCODE_DIR.exists():
        VSCODE_DIR.mkdir(parents=True)
        SETTINGS_JSON.touch()

    settings = {
        "python.defaultInterpreterPath": PYTHON,
        "python.testing.pytestEnabled": True,
    }

    with open(SETTINGS_JSON, mode="w", encoding="utf-8") as f:
        json.dump(settings, f, sort_keys=True, indent=4)


def task_dev():
    """
    Create a virtual environment & install dev dependencies.
    """

    return {
        "actions": [
            "poetry config virtualenvs.in-project true",
            "poetry install",
            (set_up_vscode),
        ],
        "file_dep": [PYPROJECT_TOML],
        "targets": [VENV_DIR, VSCODE_DIR, POETRY_LOCK],
        "clean": [
            (shutil.rmtree, (VENV_DIR,), {"ignore_errors": True}),
            (shutil.rmtree, (VSCODE_DIR,), {"ignore_errors": True}),
            (POETRY_LOCK.unlink, (), {"missing_ok": True}),
        ],
    }


def task_build():
    """
    Builds the project's sdist and wheel.
    """

    return {
        "actions": ["poetry build"],
        "file_dep": PYTHON_FILES + [PYPROJECT_TOML],
        "task_dep": ["dev"],
        "targets": [DIST_DIR],
        "clean": [
            (shutil.rmtree, (DIST_DIR,), {"ignore_errors": True}),
        ],
        "verbosity": 0,
    }


def task_test():
    """
    Runs unit tests with pytest.
    """

    return {
        "actions": [f"{PYTHON} -m pytest --cov={PROJECT_SRC} {PROJECT_TESTS}/"],
        "file_dep": PYTHON_FILES,
        "task_dep": ["dev"],
        "verbosity": 2,
    }


def task_cov():
    """
    Shows coverage report.
    """

    return {
        "actions": [f"{PYTHON} -m coverage report --show-missing"],
        "file_dep": PYTHON_FILES,
        "task_dep": ["dev", "test"],
        "targets": [COVERAGE_DATA],
        "verbosity": 2,
        "clean": [(COVERAGE_DATA.unlink, (), {"missing_ok": True})],
    }


def lint_isort():
    """
    Sorts imports using isort.
    """

    return {
        "name": "isort",
        "actions": [f"{PYTHON} -m isort ."],
        "file_dep": PYTHON_FILES,
        "task_dep": ["dev"],
    }


def lint_black():
    """
    Formats code using black.
    """

    return {
        "name": "black",
        "actions": [f"{PYTHON} -m black ."],
        "file_dep": PYTHON_FILES,
        "task_dep": ["dev"],
    }


def lint_flake8():
    """
    Lints code using flake8.
    """

    return {
        "name": "flake8",
        "actions": [f"{PYTHON} -m flake8 ."],
        "file_dep": PYTHON_FILES,
        "task_dep": ["dev"],
    }


def lint_mypy():
    """
    Type checks code using mypy.
    """

    return {
        "name": "mypy",
        "actions": [f"{PYTHON} -m mypy --install-types --non-interactive"],
        "file_dep": PYTHON_FILES,
        "task_dep": ["dev"],
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
        "task_dep": ["dev"],
        "targets": [DOCS_BUILD],
        "clean": [(shutil.rmtree, (DOCS_BUILD,), {"ignore_errors": True})],
    }
