from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
from typing import TextIO

import pytest
from pytest_mock import MockerFixture
from pytoil.environments import Poetry
from pytoil.exceptions import PoetryNotInstalledError


def test_poetry_instantiation_default() -> None:
    poetry = Poetry(root=Path("somewhere"))

    assert poetry.project_path == Path("somewhere").resolve()
    assert poetry.poetry == shutil.which("poetry")
    assert poetry.name == "poetry"
    assert poetry.executable == Path("somewhere").resolve().joinpath(".venv/bin/python")


def test_poetry_instanciation_passed() -> None:
    poetry = Poetry(root=Path("somewhere"), poetry="notpoetry")

    assert poetry.project_path == Path("somewhere").resolve()
    assert poetry.poetry == "notpoetry"
    assert poetry.name == "poetry"
    assert poetry.executable == Path("somewhere").resolve().joinpath(".venv/bin/python")


def test_poetry_repr() -> None:
    poetry = Poetry(root=Path("somewhere"), poetry="notpoetry")
    assert repr(poetry) == f"Poetry(root={Path('somewhere')!r}, poetry='notpoetry')"


def test_create_raises_not_implemented_error() -> None:
    poetry = Poetry(root=Path("somewhere"), poetry="notpoetry")

    with pytest.raises(NotImplementedError):
        poetry.create()


def test_enforce_local_config_correctly_calls_poetry(mocker: MockerFixture) -> None:
    mock = mocker.patch("pytoil.environments.poetry.subprocess.run", autospec=True)

    poetry = Poetry(root=Path("somewhere"), poetry="notpoetry")

    poetry.enforce_local_config()

    mock.assert_called_once_with(
        ["notpoetry", "config", "virtualenvs.in-project", "true", "--local"],
        cwd=poetry.project_path,
    )


def test_enforce_local_config_raises_if_poetry_not_installed() -> None:
    poetry = Poetry(root=Path("somewhere"), poetry=None)

    with pytest.raises(PoetryNotInstalledError):
        poetry.enforce_local_config()


@pytest.mark.parametrize(
    ("silent", "stdout", "stderr"),
    [
        (True, subprocess.DEVNULL, subprocess.DEVNULL),
        (False, sys.stdout, sys.stderr),
    ],
)
def test_install_correctly_calls_poetry(
    mocker: MockerFixture, silent: bool, stdout: TextIO | int, stderr: TextIO | int
) -> None:
    mock = mocker.patch("pytoil.environments.poetry.subprocess.run", autospec=True)

    poetry = Poetry(root=Path("somewhere"), poetry="notpoetry")

    # Mock out enforce local config as `install` runs this first
    mocker.patch(
        "pytoil.environments.poetry.Poetry.enforce_local_config", autospec=True
    )

    poetry.install(packages=["black", "isort", "flake8", "mypy"], silent=silent)

    mock.assert_called_once_with(
        ["notpoetry", "add", "black", "isort", "flake8", "mypy"],
        cwd=poetry.project_path,
        stdout=stdout,
        stderr=stderr,
    )


def test_install_raises_if_poetry_not_installed() -> None:
    poetry = Poetry(root=Path("somewhere"), poetry=None)

    with pytest.raises(PoetryNotInstalledError):
        poetry.install(packages=["something", "doesn't", "matter"])


@pytest.mark.parametrize(
    ("silent", "stdout", "stderr"),
    [
        (True, subprocess.DEVNULL, subprocess.DEVNULL),
        (False, sys.stdout, sys.stderr),
    ],
)
def test_install_self_correctly_calls_poetry(
    mocker: MockerFixture, silent: bool, stdout: TextIO | int, stderr: TextIO | int
) -> None:
    mock = mocker.patch("pytoil.environments.poetry.subprocess.run", autospec=True)

    poetry = Poetry(root=Path("somewhere"), poetry="notpoetry")

    # Mock out enforce local config as `install` runs this first
    mocker.patch(
        "pytoil.environments.poetry.Poetry.enforce_local_config", autospec=True
    )

    poetry.install_self(silent=silent)

    mock.assert_called_once_with(
        ["notpoetry", "install"],
        cwd=poetry.project_path,
        stdout=stdout,
        stderr=stderr,
    )


def test_install_selfraises_if_poetry_not_installed() -> None:
    poetry = Poetry(root=Path("somewhere"), poetry=None)

    with pytest.raises(PoetryNotInstalledError):
        poetry.install_self()
