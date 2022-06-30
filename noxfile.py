"""
Nox automation tasks for pytoil
"""

from __future__ import annotations

import json
import os
import shutil
import webbrowser
from pathlib import Path

import nox

# Nox config
nox.needs_version = ">=2022.1.7"
nox.options.error_on_external_run = True

# GitHub Actions
ON_CI = bool(os.getenv("CI"))

# Global project stuff
PROJECT_ROOT = Path(__file__).parent.resolve()
PROJECT_SRC = PROJECT_ROOT / "src"
PROJECT_TESTS = PROJECT_ROOT / "tests"

# Git info
DEFAULT_BRANCH = "main"

# VSCode
VSCODE_DIR = PROJECT_ROOT / ".vscode"
SETTINGS_JSON = VSCODE_DIR / "settings.json"

# Virtual environment stuff
VENV_DIR = PROJECT_ROOT / ".venv"
PYTHON = os.fsdecode(VENV_DIR / "bin" / "python")

# Python to use for non-test sessions
DEFAULT_PYTHON: str = "3.10"

# All supported python versions for pytoil
PYTHON_VERSIONS: list[str] = [
    "3.9",
    "3.10",
]

# "dev" should only be run if no virtual environment found and we're not on CI
# i.e. someone is using nox to set up their local dev environment to
# work on pytoil
if not VENV_DIR.exists() and not ON_CI:
    nox.options.sessions = ["dev"]
else:
    nox.options.sessions = ["test", "coverage", "lint", "docs"]


@nox.session(python=DEFAULT_PYTHON)
def dev(session: nox.Session) -> None:
    """
    Sets up a python dev environment for the project if one doesn't already exist.

    This session will:
    - Create a python virtualenv for the session
    - Install the `virtualenv` cli tool into this environment
    - Use `virtualenv` to create a global project virtual environment
    - Invoke the python interpreter from the global project environment to install
      the project and all it's development dependencies.
    """
    # Check if dev has been run before
    # this prevents manual running nox -s dev more than once
    # thus potentially corrupting an environment
    if VENV_DIR.exists():
        session.error(
            "There is already a virtual environment deactivate and remove it "
            "before running 'dev' again"
        )

    # Create the project virtual environment using virtualenv
    # installed into this sessions virtual environment
    # confusing but it works!
    session.install("virtualenv")
    session.run("virtualenv", os.fsdecode(VENV_DIR), silent=True)

    # Use the venv's interpreter to install the project along with
    # all it's dev dependencies, this ensure it's installed
    # in the right way
    session.run(
        PYTHON,
        "-m",
        "pip",
        "install",
        "--upgrade",
        "pip",
        "flit",
        silent=True,
        external=True,
    )
    # Flit equivalent of pip install -e .[dev]
    session.run("flit", "install", "--symlink", "--python", PYTHON, external=True)

    if bool(shutil.which("code")) or bool(shutil.which("code-insiders")):
        # Only do this is user has VSCode installed
        set_up_vscode(session)


@nox.session(python=PYTHON_VERSIONS)
def test(session: nox.Session) -> None:
    """
    Runs the test suite against all supported python versions.
    """
    session.install("--upgrade", "pip", "setuptools", "wheel")
    # Tests require the package to be installed
    session.install(".")
    session.install(
        "pytest",
        "pytest-cov",
        "pytest-mock",
        "pytest-httpx",
        "pytest-randomly",
        "freezegun",
    )

    session.run("pytest", f"--cov={PROJECT_SRC}", f"{PROJECT_TESTS}")
    session.notify("coverage")


@nox.session(python=DEFAULT_PYTHON)
def codecov(session: nox.Session) -> None:
    """
    Generate a codecov xml report for CI.
    """
    session.install("--upgrade", "pip", "setuptools", "wheel")

    session.install(".")
    session.install(
        "pytest",
        "pytest-cov",
        "pytest-mock",
        "pytest-httpx",
        "pytest-randomly",
        "freezegun",
    )

    session.run("pytest", f"--cov={PROJECT_SRC}", f"{PROJECT_TESTS}")
    session.run("coverage", "xml")


@nox.session(python=DEFAULT_PYTHON)
def coverage(session: nox.Session) -> None:
    """
    Test coverage analysis.
    """
    session.install("--upgrade", "pip", "setuptools", "wheel")
    session.install("coverage[toml]")

    session.run("coverage", "report", "--show-missing")


@nox.session(python=DEFAULT_PYTHON)
def lint(session: nox.Session) -> None:
    """
    Run pre-commit linting.
    """
    session.install("--upgrade", "pip", "setuptools", "wheel")
    session.install("pre-commit")

    session.run("pre-commit", "run", "--all-files")


@nox.session(python=DEFAULT_PYTHON)
def docs(session: nox.Session) -> None:
    """
    Builds the project documentation. Use '-- serve' to see changes live.
    """
    session.install("--upgrade", "pip", "setuptools", "wheel")
    session.install("mkdocs", "mkdocs-material")

    if "serve" in session.posargs:
        webbrowser.open(url="http://127.0.0.1:8000/pytoil/")
        session.run("mkdocs", "serve")
    else:
        session.run("mkdocs", "build", "--clean")


@nox.session
def deploy_docs(session: nox.Session) -> None:
    """
    Used by GitHub actions to deploy docs to GitHub Pages.
    """
    session.install("--upgrade", "pip", "setuptools", "wheel")
    session.install("mkdocs", "mkdocs-material")

    if ON_CI:
        session.run(
            "git",
            "remote",
            "add",
            "gh-token",
            "https://${GITHUB_TOKEN}@github.com/FollowTheProcess/pytoil.git",
            external=True,
        )
        session.run("git", "fetch", "gh-token", external=True)
        session.run("git", "fetch", "gh-token", "gh-pages:gh-pages", external=True)

        session.run("mkdocs", "gh-deploy", "-v", "--clean", "--remote-name", "gh-token")
    else:
        session.run("mkdocs", "gh-deploy")


@nox.session(python=DEFAULT_PYTHON)
def build(session: nox.Session) -> None:
    """
    Builds the package sdist and wheel.
    """
    session.install("--upgrade", "pip", "flit")
    session.install("flit")

    session.run("flit", "build")


@nox.session(python=DEFAULT_PYTHON)
def dependabot(session: nox.Session) -> None:
    """
    Runs the poormans_dependabot utility.
    """
    session.install("--upgrade", "pip", "setuptools", "wheel")
    session.install("httpx[http2]", "rtoml", "rich")

    session.run("python", "scripts/poormans_dependabot.py")


def set_up_vscode(session: nox.Session) -> None:
    """
    Helper function that will set VSCode's workspace settings
    to use the auto-created virtual environment and enable
    pytest support.

    If called, this function will only do anything if
    there aren't already VSCode workspace settings defined.

    Args:
        session (nox.Session): The enclosing nox session.
    """
    if not VSCODE_DIR.exists():
        session.log("Setting up VSCode Workspace.")
        VSCODE_DIR.mkdir(parents=True)
        SETTINGS_JSON.touch()

        settings = {
            "python.defaultInterpreterPath": PYTHON,
            "python.testing.pytestEnabled": True,
            "python.testing.pytestArgs": [PROJECT_TESTS.name],
        }

        with open(SETTINGS_JSON, mode="w", encoding="utf-8") as f:
            json.dump(settings, f, sort_keys=True, indent=4)
