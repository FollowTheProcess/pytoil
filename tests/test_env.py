"""
Tests for the virtualenv module.

Author: Tom Fleet
Created: 04/02/2021
"""

import pathlib

import pytest

import pytoil
from pytoil.env import VirtualEnv
from pytoil.exceptions import (
    MissingInterpreterError,
    TargetDirDoesNotExistError,
    VirtualenvAlreadyExistsError,
)


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


def test_virtualenv_repr():

    path = pathlib.Path("made/up/dir")

    env = VirtualEnv(basepath=path)
    env2 = VirtualEnv(basepath=path, name="dinglevenv")

    assert env.__repr__() == f"VirtualEnv(basepath={path!r}, name='.venv')"
    assert env2.__repr__() == f"VirtualEnv(basepath={path!r}, name='dinglevenv')"


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


@pytest.mark.parametrize(
    "pathlib_exists, pytoil_exists", [(True, True), (False, False)]
)
def test_virtualenv_basepath_exists_returns_correct_value(
    mocker, pathlib_exists, pytoil_exists
):

    mocker.patch(
        "pytoil.env.pathlib.Path.exists", autospec=True, return_value=pathlib_exists
    )

    env = VirtualEnv(basepath=pathlib.Path("made/up/dir"))

    assert env.basepath_exists() == pytoil_exists


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

    # Make it think the basepath does exist
    mocker.patch(
        "pytoil.env.VirtualEnv.basepath_exists", autospec=True, return_value=True
    )

    # Create the virtualenv
    env.create()

    assert env.executable == pathlib.Path("made/up/dir/.venv/bin/python").resolve()


def test_virtualenv_create_raises_if_basepath_doesnt_exist(mocker):

    env = VirtualEnv(basepath=pathlib.Path("made/up/dir"))

    # Make it think the basepath doesn't exist
    # It doesn't anyway because we've made it up but better to explicitly do it
    mocker.patch(
        "pytoil.env.VirtualEnv.basepath_exists", autospec=True, return_value=False
    )

    with pytest.raises(TargetDirDoesNotExistError):
        env.create()


def test_virtualenv_raise_for_executable_raises_when_required(mocker):

    env = VirtualEnv(basepath=pathlib.Path("made/up/dir"))

    # Make it think the basepath doesn't exist
    # It doesn't anyway because we've made it up but better to explicitly do it
    mocker.patch(
        "pytoil.env.VirtualEnv.basepath_exists", autospec=True, return_value=False
    )

    with pytest.raises(MissingInterpreterError):
        env.raise_for_executable()


def test_virtualenv_raise_for_executable_doesnt_raise_when_not_required(mocker):

    # Make it think the basepath doesn't exist
    # It doesn't anyway because we've made it up but better to explicitly do it
    mocker.patch(
        "pytoil.env.VirtualEnv.basepath_exists", autospec=True, return_value=False
    )

    # Patch out env.executable to be anything other than None and it shouldnt raise
    with mocker.patch.object(
        pytoil.env.VirtualEnv,
        "executable",
        pathlib.Path("made/up/dir/.venv/bin/python"),
    ):

        env = VirtualEnv(basepath=pathlib.Path("made/up/dir"))

        # If this raises, the test will fail
        env.raise_for_executable()
