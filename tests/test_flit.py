"""
Tests for the flit module.

Author: Tom Fleet
Created: 13/07/2021
"""

import subprocess
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from pytoil.environments import FlitEnv
from pytoil.exceptions import FlitNotInstalledError


def test_flitenv_init():

    root = Path("/Users/me/fakeproject")
    venv = FlitEnv(project_path=root)

    assert venv.project_path == root
    assert venv.executable == root.joinpath(".venv/bin/python")


def test_flitenv_repr():

    root = Path("/Users/me/fakeproject")
    venv = FlitEnv(project_path=root)

    assert repr(venv) == f"FlitEnv(project_path={root!r})"


def test_flitenv_info_name():

    root = Path("/Users/me/fakeproject")
    venv = FlitEnv(project_path=root)

    assert venv.info_name == "flit"


def test_executable_points_to_correct_path():

    root = Path("/Users/me/fakeproject")
    venv = FlitEnv(project_path=root)

    assert venv.executable == root.joinpath(".venv/bin/python")


def test_install_self_raises_if_flit_not_installed(mocker: MockerFixture):

    root = Path("/Users/me/fakeproject")
    venv = FlitEnv(project_path=root)

    mocker.patch(
        "pytoil.environments.flit.shutil.which", autospec=True, return_value=None
    )

    with pytest.raises(FlitNotInstalledError):
        venv.install_self()


def test_install_self_passes_correct_command_to_subprocess(mocker: MockerFixture):

    root = Path("/Users/me/fakeproject")
    venv = FlitEnv(project_path=root)

    mock_subprocess = mocker.patch(
        "pytoil.environments.virtualenv.subprocess.run", autospec=True
    )

    mocker.patch(
        "pytoil.environments.flit.shutil.which", autospec=True, return_value="flit"
    )

    # Trick it into thinking the venv already exists so as not
    # to raise a MissingInterpreterError
    mocker.patch(
        "pytoil.environments.virtualenv.Venv.exists", autospec=True, return_value=True
    )

    venv.install_self()

    mock_subprocess.assert_called_once_with(
        [
            "flit",
            "install",
            "--deps",
            "develop",
            "--symlink",
            "--python",
            f"{venv.executable}",
        ],
        check=True,
        cwd=venv.project_path,
    )


def test_install_self_raises_on_subprocess_error(mocker: MockerFixture):

    root = Path("/Users/me/fakeproject")
    venv = FlitEnv(project_path=root)

    mocker.patch(
        "pytoil.environments.virtualenv.subprocess.run",
        autospec=True,
        side_effect=[subprocess.CalledProcessError(-1, "cmd")],
    )

    mocker.patch(
        "pytoil.environments.flit.shutil.which", autospec=True, return_value="flit"
    )

    # Trick it into thinking the venv already exists so as not
    # to raise a MissingInterpreterError
    mocker.patch(
        "pytoil.environments.virtualenv.Venv.exists", autospec=True, return_value=True
    )

    with pytest.raises(subprocess.CalledProcessError):
        venv.install_self()
