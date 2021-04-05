"""
Nox configuration file for the project.
"""

from pathlib import Path
from typing import List

import nox

PROJECT_ROOT = Path(__file__).parent.resolve()

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
    update_seeds(session)
    session.install(".[test]")
    # Posargs allows passing of tests directly
    tests = session.posargs or ["tests/"]
    session.run("pytest", "--cov=pytoil", *tests)
    session.notify("coverage")


@nox.session(python=DEFAULT_PYTHON)
def coverage(session: nox.Session) -> None:
    """
    Test coverage analysis.
    """
    img_path = PROJECT_ROOT.joinpath("docs/img/coverage.svg")

    if not img_path.exists():
        img_path.parent.mkdir(parents=True)
        img_path.touch()

    update_seeds(session)
    session.install(".[cov]")

    session.run("coverage", "report", "--show-missing")
    session.run("coverage-badge", "-fo", f"{img_path}")


@nox.session(python=DEFAULT_PYTHON)
def lint(session: nox.Session) -> None:
    """
    Formats project with black and isort, then runs flake8 and mypy linting.
    """
    update_seeds(session)
    session.install(".[lint]")
    session.run("isort", ".")
    session.run("black", ".")
    session.run("flake8", ".")
    session.run("mypy", ".")


@nox.session(python=DEFAULT_PYTHON)
def docs(session: nox.Session) -> None:
    """
    Builds the project documentation.

    You can also serve the docs by running:

    nox -s docs -- serve
    """
    update_seeds(session)
    session.install(".[docs]")

    if "serve" in session.posargs:
        session.run("mkdocs", "serve")
    else:
        session.run("mkdocs", "build", "--clean")
