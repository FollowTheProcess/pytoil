"""
Tests for the poetry env management class.

Author: Tom Fleet
Created: 14/07/2021
"""

from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from pytoil.environments import PoetryEnv
from pytoil.exceptions import PoetryNotInstalledError


def test_poetryenv_init():

    root = Path("/Users/me/fakeproject")
    venv = PoetryEnv(project_path=root)

    assert venv.project_path == root
    assert venv.executable == root.joinpath(".venv/bin/python")


def test_poetryenv_repr():

    root = Path("/Users/me/fakeproject")
    venv = PoetryEnv(project_path=root)

    assert repr(venv) == f"PoetryEnv(project_path={root!r})"


def test_poetryenv_info_name():

    root = Path("/Users/me/fakeproject")
    venv = PoetryEnv(project_path=root)

    assert venv.info_name == "poetry"


def test_executable_points_to_correct_path():

    root = Path("/Users/me/fakeproject")
    venv = PoetryEnv(project_path=root)

    assert venv.executable == root.joinpath(".venv/bin/python")


@pytest.mark.parametrize(
    "pathlib_exists, pytoil_exists",
    [
        (True, True),
        (False, False),
    ],
)
def test_exists_returns_correct_value(
    mocker: MockerFixture, pathlib_exists, pytoil_exists
):

    root = Path("/Users/me/fakeproject")
    venv = PoetryEnv(project_path=root)

    mocker.patch(
        "pytoil.environments.poetry.Path.exists",
        autospec=True,
        return_value=pathlib_exists,
    )

    assert venv.exists() is pytoil_exists


def test_create_raises_not_implemented_error():
    """
    Create does nothing for poetry environments as
    you can't really create an environment by itself using
    poetry's model.
    """

    root = Path("/Users/me/fakeproject")
    venv = PoetryEnv(project_path=root)

    with pytest.raises(NotImplementedError):
        venv.create()


def test_raise_for_poetry_raises_if_required(mocker: MockerFixture):

    root = Path("/Users/me/fakeproject")
    venv = PoetryEnv(project_path=root)

    mocker.patch(
        "pytoil.environments.poetry.shutil.which", autospec=True, return_value=None
    )

    with pytest.raises(PoetryNotInstalledError):
        venv.raise_for_poetry()


def test_enforce_local_config_correctly_calls_poetry(mocker: MockerFixture):

    root = Path("/Users/me/fakeproject")
    venv = PoetryEnv(project_path=root)

    mock_subprocess = mocker.patch(
        "pytoil.environments.poetry.subprocess.run", autospec=True
    )

    mocker.patch(
        "pytoil.environments.poetry.shutil.which", autospec=True, return_value="poetry"
    )

    venv.enforce_local_config()

    mock_subprocess.assert_called_once_with(
        ["poetry", "config", "virtualenvs.in-project", "true", "--local"],
        check=True,
        cwd=venv.project_path,
    )


def test_install_correctly_calls_poetry(mocker: MockerFixture):

    root = Path("/Users/me/fakeproject")
    venv = PoetryEnv(project_path=root)

    mock_subprocess = mocker.patch(
        "pytoil.environments.poetry.subprocess.run", autospec=True
    )

    mocker.patch(
        "pytoil.environments.poetry.PoetryEnv.enforce_local_config", autospec=True
    )

    venv.install(packages=["test", "packages", "here"])

    mock_subprocess.assert_called_once_with(
        ["poetry", "add", "test", "packages", "here", "--quiet"],
        check=True,
        cwd=venv.project_path,
    )


def test_install_self_correctly_calls_poetry(mocker: MockerFixture):

    root = Path("/Users/me/fakeproject")
    venv = PoetryEnv(project_path=root)

    mock_subprocess = mocker.patch(
        "pytoil.environments.poetry.subprocess.run", autospec=True
    )

    mocker.patch(
        "pytoil.environments.poetry.PoetryEnv.enforce_local_config", autospec=True
    )

    venv.install_self()

    mock_subprocess.assert_called_once_with(
        ["poetry", "install", "--quiet"],
        check=True,
        cwd=venv.project_path,
        capture_output=True,
    )
