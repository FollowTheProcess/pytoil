import asyncio
import shutil
import sys
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from pytoil.environments import Poetry
from pytoil.exceptions import PoetryNotInstalledError


def test_poetry_instanciation_default():
    poetry = Poetry(root=Path("somewhere"))

    assert poetry.project_path == Path("somewhere").resolve()
    assert poetry.poetry == shutil.which("poetry")
    assert poetry.name == "poetry"
    assert poetry.executable == Path("somewhere").resolve().joinpath(".venv/bin/python")


def test_poetry_instanciation_passed():
    poetry = Poetry(root=Path("somewhere"), poetry="notpoetry")

    assert poetry.project_path == Path("somewhere").resolve()
    assert poetry.poetry == "notpoetry"
    assert poetry.name == "poetry"
    assert poetry.executable == Path("somewhere").resolve().joinpath(".venv/bin/python")


def test_poetry_repr():
    poetry = Poetry(root=Path("somewhere"), poetry="notpoetry")
    assert repr(poetry) == f"Poetry(root={Path('somewhere')!r}, poetry='notpoetry')"


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
        "pytoil.environments.poetry.aiofiles.os.path.exists",
        autospec=True,
        return_value=exists_return,
    )

    poetry = Poetry(root=Path("somewhere"), poetry="notpoetry")
    assert await poetry.exists() is exists


@pytest.mark.asyncio
async def test_create_raises_not_implemented_error():
    poetry = Poetry(root=Path("somewhere"), poetry="notpoetry")

    with pytest.raises(NotImplementedError):
        await poetry.create()


@pytest.mark.asyncio
async def test_enforce_local_config_correctly_calls_poetry(mocker: MockerFixture):
    mock = mocker.patch(
        "pytoil.environments.poetry.asyncio.create_subprocess_exec", autospec=True
    )

    poetry = Poetry(root=Path("somewhere"), poetry="notpoetry")

    await poetry.enforce_local_config()

    mock.assert_called_once_with(
        "notpoetry",
        "config",
        "virtualenvs.in-project",
        "true",
        "--local",
        cwd=poetry.project_path,
    )


@pytest.mark.asyncio
async def test_enforce_local_config_raises_if_poetry_not_installed():
    poetry = Poetry(root=Path("somewhere"), poetry=None)

    with pytest.raises(PoetryNotInstalledError):
        await poetry.enforce_local_config()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "silent, stdout, stderr",
    [
        (True, asyncio.subprocess.DEVNULL, asyncio.subprocess.DEVNULL),
        (False, sys.stdout, sys.stderr),
    ],
)
async def test_install_correctly_calls_poetry(
    mocker: MockerFixture, silent: bool, stdout, stderr
):
    mock = mocker.patch(
        "pytoil.environments.poetry.asyncio.create_subprocess_exec", autospec=True
    )

    poetry = Poetry(root=Path("somewhere"), poetry="notpoetry")

    # Mock out enforce local config as `install` runs this first
    mocker.patch(
        "pytoil.environments.poetry.Poetry.enforce_local_config", autospec=True
    )

    await poetry.install(packages=["black", "isort", "flake8", "mypy"], silent=silent)

    mock.assert_called_once_with(
        "notpoetry",
        "add",
        "black",
        "isort",
        "flake8",
        "mypy",
        cwd=poetry.project_path,
        stdout=stdout,
        stderr=stderr,
    )


@pytest.mark.asyncio
async def test_install_raises_if_poetry_not_installed():
    poetry = Poetry(root=Path("somewhere"), poetry=None)

    with pytest.raises(PoetryNotInstalledError):
        await poetry.install(packages=["something", "doesn't", "matter"])


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "silent, stdout, stderr",
    [
        (True, asyncio.subprocess.DEVNULL, asyncio.subprocess.DEVNULL),
        (False, sys.stdout, sys.stderr),
    ],
)
async def test_install_self_correctly_calls_poetry(
    mocker: MockerFixture, silent: bool, stdout, stderr
):
    mock = mocker.patch(
        "pytoil.environments.poetry.asyncio.create_subprocess_exec", autospec=True
    )

    poetry = Poetry(root=Path("somewhere"), poetry="notpoetry")

    # Mock out enforce local config as `install` runs this first
    mocker.patch(
        "pytoil.environments.poetry.Poetry.enforce_local_config", autospec=True
    )

    await poetry.install_self(silent=silent)

    mock.assert_called_once_with(
        "notpoetry",
        "install",
        cwd=poetry.project_path,
        stdout=stdout,
        stderr=stderr,
    )


@pytest.mark.asyncio
async def test_install_selfraises_if_poetry_not_installed():
    poetry = Poetry(root=Path("somewhere"), poetry=None)

    with pytest.raises(PoetryNotInstalledError):
        await poetry.install_self()
