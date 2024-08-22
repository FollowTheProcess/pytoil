"""
Maintenance tasks, driven by Nox!
"""

from __future__ import annotations

from pathlib import Path

import nox

nox.options.default_venv_backend = "uv"

ROOT = Path(__file__).parent.resolve()
SRC = ROOT / "src"
TESTS = ROOT / "tests"


@nox.session(tags=["check"])
def test(session: nox.Session) -> None:
    """
    Run the test suite
    """
    session.install(".")
    session.install(
        "pytest",
        "pytest-cov",
        "pytest-mock",
        "pytest-httpx",
        "pytest-randomly",
        "covdefaults",
        "coverage[toml]",
        "freezegun",
    )
    session.run("pytest", "--cov", f"{SRC}", f"{TESTS}")

    if "cover" in session.posargs:
        session.run("coverage", "xml")


@nox.session(tags=["check"])
def lint(session: nox.Session) -> None:
    """
    Lint the project
    """
    session.install("pre-commit")
    session.run("pre-commit", "run", "--all-files")


@nox.session
def docs(session: nox.Session) -> None:
    """
    Build the documentation
    """
    session.install("mkdocs", "mkdocs-material")
    session.run("mkdocs", "build", "--clean")

    if "serve" in session.posargs:
        session.run("mkdocs", "serve")
    elif "deploy" in session.posargs:
        session.run("mkdocs", "gh-deploy", "--force")


@nox.session
def build(session: nox.Session) -> None:
    """
    Build the sdist and wheel
    """
    session.install("build")
    session.run("python", "-m", "build", ".")
