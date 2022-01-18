import asyncio
import sys
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from pytoil.environments import Venv


def test_virtualenv():
    venv = Venv(root=Path("somewhere"))

    assert venv.project_path == Path("somewhere").resolve()
    assert venv.executable == Path("somewhere").resolve().joinpath(".venv/bin/python")
    assert venv.name == "venv"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exists_return, exists",
    [
        (True, True),
        (False, False),
    ],
)
async def test_exists_returns_correct_value(
    mocker: MockerFixture, exists_return, exists: bool
):

    # Ensure aiofiles.os.path.exists returns what we want it to
    mocker.patch(
        "pytoil.environments.virtualenv.aiofiles.os.path.exists",
        autospec=True,
        return_value=exists_return,
    )

    venv = Venv(root=Path("somewhere"))
    assert await venv.exists() is exists


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "silent, stdout, stderr",
    [
        (True, asyncio.subprocess.DEVNULL, asyncio.subprocess.DEVNULL),
        (False, sys.stdout, sys.stderr),
    ],
)
async def test_install_calls_pip_correctly(
    mocker: MockerFixture, silent: bool, stdout, stderr
):
    mock = mocker.patch(
        "pytoil.environments.virtualenv.asyncio.create_subprocess_exec",
        autospec=True,
    )

    venv = Venv(root=Path("somewhere"))

    await venv.install(["black", "mypy", "isort", "flake8"], silent=silent)

    mock.assert_called_once_with(
        f"{venv.executable}",
        "-m",
        "pip",
        "install",
        "black",
        "mypy",
        "isort",
        "flake8",
        cwd=venv.project_path,
        stdout=stdout,
        stderr=stderr,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "silent, stdout, stderr",
    [
        (True, asyncio.subprocess.DEVNULL, asyncio.subprocess.DEVNULL),
        (False, sys.stdout, sys.stderr),
    ],
)
async def test_install_self_calls_pip_correctly(
    mocker: MockerFixture, silent: bool, stdout, stderr
):
    mock = mocker.patch(
        "pytoil.environments.virtualenv.asyncio.create_subprocess_exec",
        autospec=True,
    )

    # Make it think there's already a venv
    mocker.patch(
        "pytoil.environments.virtualenv.Venv.exists",
        autospec=True,
        return_value=True,
    )

    venv = Venv(root=Path("somewhere"))

    await venv.install_self(silent=silent)

    mock.assert_called_once_with(
        f"{venv.executable}",
        "-m",
        "pip",
        "install",
        "-e",
        ".[dev]",
        cwd=venv.project_path,
        stdout=stdout,
        stderr=stderr,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "silent, stdout, stderr",
    [
        (True, asyncio.subprocess.DEVNULL, asyncio.subprocess.DEVNULL),
        (False, sys.stdout, sys.stderr),
    ],
)
async def test_install_self_creates_venv_if_not_one_already(
    mocker: MockerFixture, silent: bool, stdout, stderr
):
    mock = mocker.patch(
        "pytoil.environments.virtualenv.asyncio.create_subprocess_exec",
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

    await venv.install_self(silent=silent)

    mock_create.assert_called_once()

    mock.assert_called_once_with(
        f"{venv.executable}",
        "-m",
        "pip",
        "install",
        "-e",
        ".[dev]",
        cwd=venv.project_path,
        stdout=stdout,
        stderr=stderr,
    )
