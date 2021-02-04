"""
Tests for the virtualenv module.

Author: Tom Fleet
Created: 04/02/2021
"""

import pathlib

import pytest

from pytoil.env import VirtualEnv
from pytoil.exceptions import VirtualenvAlreadyExistsError


def test_virtualenv_init():

    env = VirtualEnv(basepath=pathlib.Path("made/up/dir"))
    env2 = VirtualEnv(basepath=pathlib.Path("made/up/dir"), name="dinglevenv")

    assert env.basepath == pathlib.Path("made/up/dir")
    assert env.name == ".venv"  # Default name
    assert env.path == pathlib.Path("made/up/dir").joinpath(".venv")
    assert env.executable is None

    assert env2.basepath == pathlib.Path("made/up/dir")
    assert env2.name == "dinglevenv"  # Specified name
    assert env2.path == pathlib.Path("made/up/dir").joinpath("dinglevenv")
    assert env2.executable is None


def test_virtualenv_executable_setter():

    env = VirtualEnv(basepath=pathlib.Path("made/up/dir"))

    # Ensure executable starts as None
    assert env.executable is None

    # Create a new fake executable path
    new_executable = pathlib.Path(env.path.joinpath("bin/python"))

    # Set the env executable to this fake path
    env.executable = new_executable

    assert env.executable == new_executable


@pytest.mark.parametrize(
    "pathlib_exists, pytoil_exists", [(True, True), (False, False)]
)
def test_virtualenv_exists_returns_correct_value(mocker, pathlib_exists, pytoil_exists):

    mocker.patch(
        "pytoil.env.pathlib.Path.exists", autospec=True, return_value=pathlib_exists
    )

    env = VirtualEnv(basepath=pathlib.Path("made/up/dir"))

    assert env.exists() == pytoil_exists


def test_virtualenv_create_raises_if_already_exists(mocker):

    env = VirtualEnv(basepath=pathlib.Path("made/up/dir"))

    mocker.patch("pytoil.env.VirtualEnv.exists", autospec=True, return_value=True)

    with pytest.raises(VirtualenvAlreadyExistsError):
        env.create()


def test_virtualenv_create_updates_executable_on_success(mocker):

    env = VirtualEnv(basepath=pathlib.Path("made/up/dir"))

    # Patch out the actual virtualenv cli run
    mocker.patch(
        "pytoil.env.virtualenv.cli_run", autospec=True, return_value="Success!"
    )
    # Make it think the virtualenv does not already exist
    mocker.patch("pytoil.env.VirtualEnv.exists", autospec=True, return_value=False)

    # Create the virtualenv
    env.create()

    assert env.executable == pathlib.Path("made/up/dir/.venv/bin/python")
