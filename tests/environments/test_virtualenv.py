from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import TextIO

import pytest
from pytest_mock import MockerFixture
from pytoil.environments import Venv


def test_virtualenv() -> None:
    venv = Venv(root=Path("somewhere"))

    assert venv.project_path == Path("somewhere").resolve()
    assert venv.executable == Path("somewhere").resolve().joinpath(".venv/bin/python")
    assert venv.name == "venv"


def test_virtualenv_repr() -> None:
    venv = Venv(root=Path("somewhere"))
    assert repr(venv) == f"Venv(root={Path('somewhere')!r})"


@pytest.mark.parametrize(
    ("silent", "stdout", "stderr"),
    [
        (True, subprocess.DEVNULL, subprocess.DEVNULL),
        (False, sys.stdout, sys.stderr),
    ],
)
def test_install_calls_pip_correctly(
    mocker: MockerFixture, silent: bool, stdout: TextIO | int, stderr: TextIO | int
) -> None:
    mock = mocker.patch(
        "pytoil.environments.virtualenv.subprocess.run",
        autospec=True,
    )

    venv = Venv(root=Path("somewhere"))

    venv.install(["black", "mypy", "isort", "flake8"], silent=silent)

    mock.assert_called_once_with(
        [
            f"{venv.executable}",
            "-m",
            "pip",
            "install",
            "black",
            "mypy",
            "isort",
            "flake8",
        ],
        cwd=venv.project_path,
        stdout=stdout,
        stderr=stderr,
    )


@pytest.mark.parametrize(
    ("silent", "stdout", "stderr"),
    [
        (True, subprocess.DEVNULL, subprocess.DEVNULL),
        (False, sys.stdout, sys.stderr),
    ],
)
def test_install_self_calls_pip_correctly(
    mocker: MockerFixture, silent: bool, stdout: TextIO | int, stderr: TextIO | int
) -> None:
    mock = mocker.patch(
        "pytoil.environments.virtualenv.subprocess.run",
        autospec=True,
    )

    # Make it think there's already a venv
    mocker.patch(
        "pytoil.environments.virtualenv.Venv.exists",
        autospec=True,
        return_value=True,
    )

    venv = Venv(root=Path("somewhere"))

    venv.install_self(silent=silent)

    mock.assert_called_once_with(
        [f"{venv.executable}", "-m", "pip", "install", "-e", ".[dev]"],
        cwd=venv.project_path,
        stdout=stdout,
        stderr=stderr,
    )


@pytest.mark.parametrize(
    ("silent", "stdout", "stderr"),
    [
        (True, subprocess.DEVNULL, subprocess.DEVNULL),
        (False, sys.stdout, sys.stderr),
    ],
)
def test_install_self_creates_venv_if_not_one_already(
    mocker: MockerFixture, silent: bool, stdout: TextIO | int, stderr: TextIO | int
) -> None:
    mock = mocker.patch(
        "pytoil.environments.virtualenv.subprocess.run",
        autospec=True,
    )

    # Make it think there isn't a venv
    mocker.patch(
        "pytoil.environments.virtualenv.Venv.exists",
        autospec=True,
        return_value=False,
    )

    # Mock out the venv.create method
    mock_create = mocker.patch(
        "pytoil.environments.virtualenv.Venv.create", autospec=True
    )

    venv = Venv(root=Path("somewhere"))

    venv.install_self(silent=silent)

    mock_create.assert_called_once()

    mock.assert_called_once_with(
        [f"{venv.executable}", "-m", "pip", "install", "-e", ".[dev]"],
        cwd=venv.project_path,
        stdout=stdout,
        stderr=stderr,
    )
