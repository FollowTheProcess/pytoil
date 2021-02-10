"""
Tests for the CondaEnv management.

Author: Tom Fleet
Created: 10/02/2021
"""

import subprocess
from typing import NamedTuple

import pytest

from pytoil.env import CondaEnv
from pytoil.exceptions import CondaNotInstalledError, VirtualenvAlreadyExistsError


def test_condaenv_init():

    env = CondaEnv(name="sillyenv")

    assert env.name == "sillyenv"


def test_condaenv_repr():

    env = CondaEnv(name="sillyenv")

    assert env.__repr__() == "CondaEnv(name='sillyenv')"


def test_condaenv_raise_for_conda_raises_when_required(mocker):

    # Patch out shutil.which so it returns what we want it to
    mocker.patch("pytoil.env.shutil.which", autospec=True, return_value=False)

    env = CondaEnv(name="sillyenv")

    with pytest.raises(CondaNotInstalledError):
        env.raise_for_conda()


def test_condaenv_raise_for_conda_doesnt_raise_when_required(mocker):

    mocker.patch("pytoil.env.shutil.which", autospec=True, return_value=True)

    env = CondaEnv(name="sillyenv")

    # Test will fail if this raises
    env.raise_for_conda()


@pytest.mark.parametrize(
    "name, exists",
    [
        ("SiLLyEnv", True),
        ("condaenv", True),
        ("here", True),
        ("MissInG", False),
        ("DefinitelyNot_Here", False),
        ("ReallyNotHere", False),
    ],
)
def test_condaenv_exists(mocker, name, exists):
    class FakeStdOut(NamedTuple):
        # we need this so the returned object from subprocess.run
        # has a `.stdout` attribute
        stdout: str = """Hello. This is the fake stdout. Here are some environment names:
            sillyenv, condaenv, here"""

    mock_subprocess = mocker.patch(
        "pytoil.env.subprocess.run", autospec=True, return_value=FakeStdOut()
    )

    env = CondaEnv(name=name)

    assert env.exists() is exists

    mock_subprocess.assert_called_once_with(
        ["conda", "env", "list"], check=True, capture_output=True, encoding="utf-8"
    )


def test_condaenv_exists_raises_on_subprocess_error(mocker):

    mocker.patch(
        "pytoil.env.subprocess.run",
        autospec=True,
        side_effect=[subprocess.CalledProcessError(-1, "cmd")],
    )

    with pytest.raises(subprocess.CalledProcessError):
        env = CondaEnv(name="sillyenv")
        env.exists()


@pytest.mark.parametrize(
    "packages, name, expected_cmd",
    [
        (None, "sillyenv", ["conda", "create", "-y", "--name", "sillyenv", "python=3"]),
        (
            ["black", "pandas>=1.1.3", "numpy"],
            "dingleenv",
            [
                "conda",
                "create",
                "-y",
                "--name",
                "dingleenv",
                "python=3",
                "black",
                "pandas>=1.1.3",
                "numpy",
            ],
        ),
    ],
)
def test_condaenv_create_is_correctly_called(mocker, packages, name, expected_cmd):

    # Trick the test into thinking the environment doesn't already exist
    mocker.patch("pytoil.env.CondaEnv.exists", autospec=True, return_value=False)

    mock_subprocess = mocker.patch("pytoil.env.subprocess.run", autospec=True)

    env = CondaEnv(name=name)

    env.create(packages=packages)

    mock_subprocess.assert_called_once_with(expected_cmd, check=True)


def test_condaenv_create_raises_if_already_exists(mocker):

    # Trick the test into thinking the environment already exists
    mocker.patch("pytoil.env.CondaEnv.exists", autospec=True, return_value=True)

    with pytest.raises(VirtualenvAlreadyExistsError):
        env = CondaEnv(name="i_already_exist")
        env.create()


def test_condaenv_create_raises_on_subprocess_error(mocker):

    mocker.patch("pytoil.env.CondaEnv.exists", autospec=True, return_value=False)

    mocker.patch(
        "pytoil.env.subprocess.run",
        autospec=True,
        side_effect=[subprocess.CalledProcessError(-1, "cmd")],
    )

    with pytest.raises(subprocess.CalledProcessError):
        env = CondaEnv(name="error")
        env.create()
