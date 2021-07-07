"""
Nox configuration file for the project.
"""

import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List

import nox

# Minimum nox version
nox.needs_version = ">=2021.6.6"

# GitHub Actions
ON_CI = bool(os.getenv("CI"))

PROJECT_ROOT = Path(__file__).parent.resolve()
PROJECT_SRC = PROJECT_ROOT / "pytoil"
PROJECT_TESTS = PROJECT_ROOT / "tests"

COVERAGE_BADGE = PROJECT_ROOT / "docs" / "img" / "coverage.svg"

DEFAULT_PYTHON: str = "3.9"

PYTHON_VERSIONS: List[str] = [
    "3.8",
    "3.9",
]

SEEDS: List[str] = [
    "pip",
    "setuptools",
    "wheel",
]

# Dependencies for each of the nox session names
# These names must be identical to the names of the defined nox sessions
SESSION_REQUIREMENTS: Dict[str, List[str]] = {
    "test": [
        "pytest",
        "pytest-cov",
        "pytest-httpx",
        "pytest-mock",
        "coverage",
        "toml",
    ],
    "lint": [
        "flake8",
        "isort",
        "black",
        "mypy",
    ],
    "docs": [
        "mkdocs",
        "mkdocs-material",
        "mkdocstrings",
        "markdown-include",
        "livereload",
    ],
    "coverage": [
        "coverage",
        "coverage-badge",
        "toml",
    ],
}


def poetry_install(session: nox.Session, *args: str, **kwargs: Any) -> None:
    """
    Install packages constrained by Poetry's lock file.

    This function is a wrapper for nox.Session.install. It
    invokes pip to install packages inside of the session's virtualenv.

    Additionally, pip is passed a constraints file generated from
    Poetry's lock file, to ensure that the packages are pinned to the
    versions specified in poetry.lock.

    This allows you to manage the
    packages as Poetry development dependencies.

    Args:
        session (nox.Session): The wrapping nox Session.
        args (str): List of packages to install.
        kwargs: Keyword arguments passed to session.install.
    """

    with tempfile.NamedTemporaryFile() as requirements:
        session.run(
            "poetry",
            "export",
            "--dev",
            "--format=requirements.txt",
            f"--output={requirements.name}",
            "--without-hashes",
            external=True,
            silent=True,
        )
        session.install(f"--constraint={requirements.name}", *args, **kwargs)


def update_seeds(session: nox.Session) -> None:
    """
    Helper function to update the core installation seed packages
    to their latest versions in each session.
    Args:
        session (nox.Session): The nox session currently running.
    """

    session.install("--upgrade", *SEEDS)


@nox.session(python=PYTHON_VERSIONS)
def test(session: nox.Session) -> None:
    """
    Runs the test suite against all supported python versions.
    """

    test_requirements = SESSION_REQUIREMENTS.get("test", [""])

    update_seeds(session)
    # Tests require the package to be installed
    session.run("poetry", "install", "--no-dev", external=True, silent=True)
    poetry_install(session, *test_requirements)

    session.run("pytest", f"--cov={PROJECT_SRC}", f"{PROJECT_TESTS}/")
    session.notify("coverage")


@nox.session(python=DEFAULT_PYTHON)
def coverage(session: nox.Session) -> None:
    """
    Test coverage analysis.
    """

    coverage_requirements = SESSION_REQUIREMENTS.get("coverage", [""])

    img_path = COVERAGE_BADGE

    if not img_path.exists():
        img_path.parent.mkdir(parents=True)
        img_path.touch()

    update_seeds(session)
    poetry_install(session, *coverage_requirements)

    session.run("coverage", "report", "--show-missing")
    session.run("coverage-badge", "-fo", f"{img_path}")


@nox.session(python=DEFAULT_PYTHON)
def lint(session: nox.Session) -> None:
    """
    Formats project with black and isort, then runs flake8 and mypy linting.
    """

    lint_requirements = SESSION_REQUIREMENTS.get("lint", [""])

    update_seeds(session)
    poetry_install(session, *lint_requirements)

    # If we're on CI, run in check mode so build fails if formatting isn't correct
    if ON_CI:
        session.run("isort", ".", "--check")
        session.run("black", ".", "--check")
    else:
        # If local, go ahead and fix formatting
        session.run("isort", ".")
        session.run("black", ".")

    session.run("flake8", ".")
    session.run("mypy", "--install-types")


@nox.session(python=DEFAULT_PYTHON)
def docs(session: nox.Session) -> None:
    """
    Builds the project documentation.
    """

    docs_requirements = SESSION_REQUIREMENTS.get("docs", [""])

    update_seeds(session)
    poetry_install(session, *docs_requirements)

    session.run("mkdocs", "build", "--clean")
