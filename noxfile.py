"""
Nox configuration file for the project.
"""

import tempfile
from pathlib import Path
from typing import Any, List

import nox

PROJECT_ROOT = Path(__file__).parent.resolve()

PYTHON_VERSIONS: List[str] = [
    "3.8",
    "3.9",
]
TEST_REQUIREMENTS: List[str] = [
    "pytest",
    "pytest-cov",
    "pytest-mock",
    "pytest-httpx",
]
COV_REQUIREMENTS: List[str] = [
    "coverage[toml]",
    "coverage-badge",
]
LINT_REQUIREMENTS: List[str] = [
    "isort",
    "black",
    "flake8",
    "mypy",
]
DOCS_REQUIREMENTS: List[str] = [
    "mkdocs",
    "mkdocs-material",
    "mkdocstrings",
    "markdown_include",
]


def poetry_install(session: nox.Session, *args: str, **kwargs: Any) -> None:
    """
    Function that allows using poetry's lock file as the root dependency
    management system from which to install dependencies.

    Args:
        session (nox.Session): The nox session currently running.
        *args (str): Any arguments to be passed to 'pip install' i.e. packages.
        **kwargs (Any): Keyword arguments to be passed to nox.
    """
    with tempfile.NamedTemporaryFile() as requirements:
        session.run(
            "poetry",
            "export",
            "--dev",
            "--without-hashes",
            "--format=requirements.txt",
            f"--output={requirements.name}",
            external=True,
        )
        session.install(f"--constraint={requirements.name}", *args, **kwargs)


@nox.session(python=PYTHON_VERSIONS)
def test(session: nox.Session) -> None:
    """
    Runs the test suite against all specified python versions.
    """
    session.install("--upgrade", "pip", "setuptools", "wheel")
    session.run("poetry", "install", "--no-dev", external=True)
    poetry_install(session, *TEST_REQUIREMENTS)
    # Posargs allows passing of tests directly
    tests = session.posargs or ["tests/"]
    session.run("pytest", "--cov=pytoil", *tests)


@nox.session()
def coverage(session: nox.Session) -> None:
    """
    Test coverage analysis.
    """
    img_path = PROJECT_ROOT.joinpath("docs/img/coverage.svg")

    if not img_path.exists():
        img_path.parent.mkdir(parents=True)
        img_path.touch()

    session.install("--upgrade", "pip", "setuptools", "wheel")
    poetry_install(session, *COV_REQUIREMENTS)

    session.run("coverage", "report", "--show-missing", "--fail-under=90")
    session.run("coverage-badge", "-fo", f"{img_path}")


@nox.session()
def lint(session: nox.Session) -> None:
    """
    Formats project with black and isort, then runs flake8 and mypy linting.
    """
    session.install("--upgrade", "pip", "setuptools", "wheel")
    poetry_install(session, *LINT_REQUIREMENTS)
    session.run("isort", ".")
    session.run("black", ".")
    session.run("flake8", ".")
    session.run("mypy", ".")


@nox.session()
def docs(session: nox.Session) -> None:
    """
    Builds the project documentation.

    You can also serve the docs by running:

    nox -s docs -- serve
    """
    session.install("--upgrade", "pip", "setuptools", "wheel")
    poetry_install(session, *DOCS_REQUIREMENTS)

    if "serve" in session.posargs:
        session.run("mkdocs", "serve")
    else:
        session.run("mkdocs", "build", "--clean")
