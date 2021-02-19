"""
Tests for the CondaEnv management.

Author: Tom Fleet
Created: 10/02/2021
"""

import pathlib
import subprocess
from typing import List, NamedTuple

import pytest

from pytoil.env import CondaEnv
from pytoil.exceptions import (
    BadEnvironmentFileError,
    CondaNotInstalledError,
    VirtualenvAlreadyExistsError,
    VirtualenvDoesNotExistError,
)


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
        (
            None,
            "sillyenv",
            [
                "conda",
                "create",
                "-y",
                "--name",
                "sillyenv",
                "python=3",
            ],
        ),
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


def test_condaenv_create_from_yml_passes_correct_command(mocker, temp_environment_yml):

    # Make it think the environment doesn't already exist
    mocker.patch("pytoil.env.CondaEnv.exists", autospec=True, return_value=False)

    # Mock out the actual call to conda
    mock_subprocess = mocker.patch("pytoil.env.subprocess.run", autospec=True)

    expected_cmd: List[str] = [
        "conda",
        "env",
        "create",
        "-y",
        "--file",
        f"{str(temp_environment_yml.resolve())}",
    ]

    CondaEnv.create_from_yml(fp=temp_environment_yml)

    mock_subprocess.assert_called_once_with(expected_cmd, check=True)


def test_condaenv_create_from_yml_raises_on_missing_file(mocker):

    mocker.patch("pytoil.env.CondaEnv.exists", autospec=True, return_value=False)

    missing_env_file = pathlib.Path("definitely/not/here.yml")

    with pytest.raises(FileNotFoundError):
        CondaEnv.create_from_yml(fp=missing_env_file)


def test_condaenv_create_from_yml_raises_on_invalid_formatted_yml(
    mocker, bad_temp_environment_yml, bad_temp_environment_yml_2
):

    mocker.patch("pytoil.env.CondaEnv.exists", autospec=True, return_value=False)

    with pytest.raises(BadEnvironmentFileError):
        CondaEnv.create_from_yml(fp=bad_temp_environment_yml)

    with pytest.raises(BadEnvironmentFileError):
        CondaEnv.create_from_yml(fp=bad_temp_environment_yml_2)


def test_condaenv_create_from_yml_raises_if_env_already_exists(
    mocker, temp_environment_yml
):

    mocker.patch("pytoil.env.CondaEnv.exists", autospec=True, return_value=True)

    with pytest.raises(VirtualenvAlreadyExistsError):
        CondaEnv.create_from_yml(temp_environment_yml)


def test_condaenv_create_from_yml_raises_on_subprocess_error(
    mocker, temp_environment_yml
):

    mocker.patch("pytoil.env.CondaEnv.exists", autospec=True, return_value=False)

    mocker.patch(
        "pytoil.env.subprocess.run",
        autospec=True,
        side_effect=[subprocess.CalledProcessError(-1, "cmd")],
    )

    with pytest.raises(subprocess.CalledProcessError):
        CondaEnv.create_from_yml(fp=temp_environment_yml)


@pytest.mark.parametrize(
    "name, packages",
    [
        ("sillyenv", ["numpy", "pandas", "requests"]),
        ("dingleenv", ["black", "mypy", "dinglepython"]),
        ("blah", ["altair", "matplotlib", "seaborn"]),
    ],
)
def test_condaenv_install_passes_correct_command(mocker, name, packages):

    mocker.patch("pytoil.env.CondaEnv.exists", autospec=True, return_value=True)

    mock_subprocess = mocker.patch("pytoil.env.subprocess.run", autospec=True)

    expected_cmd: List[str] = [
        "conda",
        "install",
        "--name",
        name,
        "-y",
    ]

    expected_cmd.extend(packages)

    env = CondaEnv(name=name)

    env.install(packages=packages)

    mock_subprocess.assert_called_once_with(expected_cmd, check=True)


def test_condaenv_install_raises_if_environment_doesnt_exist(mocker):

    mocker.patch("pytoil.env.CondaEnv.exists", autospec=True, return_value=False)

    with pytest.raises(VirtualenvDoesNotExistError):
        env = CondaEnv(name="missing")
        env.install(["black", "mypy", "pandas"])


def test_condaenv_install_raises_on_subprocess_error(mocker):

    mocker.patch("pytoil.env.CondaEnv.exists", autospec=True, return_value=True)

    mocker.patch(
        "pytoil.env.subprocess.run",
        autospec=True,
        side_effect=[subprocess.CalledProcessError(-1, "cmd")],
    )

    with pytest.raises(subprocess.CalledProcessError):
        env = CondaEnv(name="error")
        env.install(["pandas", "numpy"])


def test_condaenv_export_yml_correctly_calls_conda_env(mocker):

    mocker.patch("pytoil.env.CondaEnv.exists", autospec=True, return_value=True)

    mock_subprocess = mocker.patch("pytoil.env.subprocess.run", autospec=True)

    expected_cmd: List[str] = [
        "conda",
        "env",
        "export",
        "--name",
        "condingle",
        ">",
        "/Users/me/projects/condaproject/environment.yml",
    ]

    env = CondaEnv(name="condingle")

    env.export_yml(fp=pathlib.Path("/Users/me/projects/condaproject"))

    mock_subprocess.assert_called_once_with(expected_cmd, check=True)


def test_condaenv_export_yml_raises_on_missing_env(mocker):

    mocker.patch("pytoil.env.CondaEnv.exists", autospec=True, return_value=False)

    mocker.patch("pytoil.env.subprocess.run", autospec=True)

    with pytest.raises(VirtualenvDoesNotExistError):
        env = CondaEnv(name="condingle")
        env.export_yml(fp=pathlib.Path("/Users/me/projects/condaproject"))


def test_condaenv_export_yml_raises_on_subprocess_error(mocker):

    mocker.patch("pytoil.env.CondaEnv.exists", autospec=True, return_value=True)

    mocker.patch(
        "pytoil.env.subprocess.run",
        autospec=True,
        side_effect=[subprocess.CalledProcessError(-1, "cmd")],
    )

    with pytest.raises(subprocess.CalledProcessError):
        env = CondaEnv(name="condingle")
        env.export_yml(fp=pathlib.Path("/Users/me/projects/condaproject"))
