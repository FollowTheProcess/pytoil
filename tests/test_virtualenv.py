"""
Tests for the virtualenv module.

Author: Tom Fleet
Created: 04/02/2021
"""

import pathlib
import subprocess

import pytest
from pytest_mock import MockerFixture

import pytoil
from pytoil.environments import VirtualEnv
from pytoil.exceptions import MissingInterpreterError, VirtualenvAlreadyExistsError


def test_virtualenv_init():

    fake_project = pathlib.Path("/Users/me/projects/fakeproject")

    env = VirtualEnv(project_path=fake_project)

    assert env.project_path == fake_project.resolve()
    assert env.executable == fake_project.resolve().joinpath(".venv/bin/python")


def test_virtualenv_repr():

    fake_project = pathlib.Path("/Users/me/projects/fakeproject")

    env = VirtualEnv(project_path=fake_project)

    assert env.__repr__() == f"VirtualEnv(project_path={fake_project.resolve()!r})"


def test_virtualenv_executable_points_to_correct_path():

    fake_project = pathlib.Path("/Users/me/projects/fakeproject")

    env = VirtualEnv(project_path=fake_project)

    assert env.executable == fake_project.resolve().joinpath(".venv/bin/python")


@pytest.mark.parametrize(
    "pathlib_exists, pytoil_exists", [(True, True), (False, False)]
)
def test_virtualenv_exists_returns_correct_value(
    mocker: MockerFixture, pathlib_exists, pytoil_exists
):

    fake_project = pathlib.Path("/Users/me/projects/fakeproject")

    mocker.patch(
        "pytoil.environments.venv.pathlib.Path.exists",
        autospec=True,
        return_value=pathlib_exists,
    )

    env = VirtualEnv(project_path=fake_project)

    assert env.exists() == pytoil_exists


def test_virtualenv_create_raises_if_already_exists(mocker: MockerFixture):

    fake_project = pathlib.Path("/Users/me/projects/fakeproject")

    env = VirtualEnv(project_path=fake_project)

    mocker.patch(
        "pytoil.environments.VirtualEnv.exists", autospec=True, return_value=True
    )

    with pytest.raises(VirtualenvAlreadyExistsError):
        env.create()


def test_virtualenv_create_correctly_calls_cli_run(mocker: MockerFixture):

    fake_project = pathlib.Path("/Users/me/projects/fakeproject")

    env = VirtualEnv(project_path=fake_project)

    mocker.patch(
        "pytoil.environments.VirtualEnv.exists", autospec=True, return_value=False
    )

    mock_cli_run = mocker.patch(
        "pytoil.environments.venv.virtualenv.cli_run", autospec=True, return_value=None
    )

    env.create()

    mock_cli_run.assert_called_once_with(
        [f"{fake_project.resolve().joinpath('.venv')}"]
    )


def test_virtualenv_update_seeds_raises_on_subprocess_error(mocker: MockerFixture):

    fake_project = pathlib.Path("/Users/me/projects/fakeproject")

    # Patch out exists so it thinks we have a valid executable
    mocker.patch(
        "pytoil.environments.venv.VirtualEnv.exists", autospec=True, return_value=True
    )

    # Mock calling pip but have it raise
    mock_subprocess = mocker.patch(
        "pytoil.environments.venv.subprocess.run",
        autospec=True,
        side_effect=[subprocess.CalledProcessError(-1, "cmd")],
    )

    with pytest.raises(subprocess.CalledProcessError):
        env = VirtualEnv(project_path=fake_project)
        env.update_seeds()

        # Assert pip would have been called with correct args
        mock_subprocess.assert_called_once_with(
            [
                f"{env.executable}",
                "-m",
                "pip",
                "install",
                "--upgrade",
                "pip",
                "setuptools",
                "wheel",
            ],
            check=True,
        )


def test_virtualenv_update_seeds_raises_on_missing_interpreter(mocker: MockerFixture):

    fake_project = pathlib.Path("/Users/me/projects/fakeproject")

    # Patch out exists so it thinks we dont have a valid executable
    mocker.patch(
        "pytoil.environments.venv.VirtualEnv.exists", autospec=True, return_value=False
    )

    env = VirtualEnv(project_path=fake_project)

    with pytest.raises(MissingInterpreterError):
        env.update_seeds()


def test_virtualenv_install_passes_correct_command(mocker: MockerFixture):
    """
    Tests that the correct command is constructed and sent to pip.

    We of course don't actually create a virtualenv, we just mock env.executable to be
    the pathlib.Path of this file because then it will exist and not raise any
    exceptions.

    We also patch out the actual call to pip so nothing is performed.
    The purpose of this test is to ensure the method correctly constructs
    the arguments to pass into subprocess.run.
    """

    # Force the executable property to be what we want so we can check output
    with mocker.patch.object(
        pytoil.environments.VirtualEnv,
        "executable",
        pathlib.Path("made/up/dir/.venv/bin/python").resolve(),
    ):
        # This doesnt actually matter, just has to be something
        env = VirtualEnv(project_path=pathlib.Path("made/up/dir"))

        # Mock the call to update_seeds contained within install
        mocker.patch(
            "pytoil.environments.VirtualEnv.update_seeds",
            autospec=True,
            return_value=None,
        )

        # Mock calling pip
        mock_subprocess = mocker.patch(
            "pytoil.environments.venv.subprocess.run",
            autospec=True,
        )

        # Call our install method with the parametrized arguments
        env.install(
            packages=["black", "mypy>=0.790", "numpy>1.0.1,<=1.4", "pandas>=1.2.0"]
        )

        expected_cmd = [
            f"{env.project_path.joinpath('.venv/bin/python')}",
            "-m",
            "pip",
            "install",
            "black",
            "mypy>=0.790",
            "numpy>1.0.1,<=1.4",
            "pandas>=1.2.0",
        ]

        # Assert pip would have been called with correct args
        mock_subprocess.assert_called_once_with(
            expected_cmd,
            check=True,
        )


def test_virtualenv_install_raises_on_subprocess_error(mocker: MockerFixture):
    """
    Done as a parametrized test so that we can be sure it raises regardless
    of what args passed so long as the args are valid.
    """

    # Force the executable property to be what we want so we can check output
    with mocker.patch.object(
        pytoil.environments.VirtualEnv,
        "executable",
        pathlib.Path("made/up/dir/.venv/bin/python").resolve(),
    ):

        # Mock the call to update_seeds contained within install
        mocker.patch(
            "pytoil.environments.VirtualEnv.update_seeds",
            autospec=True,
            return_value=None,
        )

        # Mock calling pip, but have it raise
        mocker.patch(
            "pytoil.environments.venv.subprocess.run",
            autospec=True,
            side_effect=[subprocess.CalledProcessError(-1, "cmd")],
        )

        with pytest.raises(subprocess.CalledProcessError):
            # This doesnt actually matter, just has to be something
            env = VirtualEnv(project_path=pathlib.Path("made/up/dir"))

            env.install(packages=["pandas", "requests", "pytoil"])


def test_virtualenv_create_with_packages_correctly_installs_packages(
    mocker: MockerFixture,
):

    fake_project = pathlib.Path("/Users/me/projects/fakeproject")

    env = VirtualEnv(project_path=fake_project)

    mocker.patch(
        "pytoil.environments.VirtualEnv.exists", autospec=True, return_value=False
    )

    mock_cli_run = mocker.patch(
        "pytoil.environments.venv.virtualenv.cli_run", autospec=True, return_value=None
    )

    mock_install = mocker.patch(
        "pytoil.environments.venv.VirtualEnv.install", autospec=True
    )

    env.create(packages=["black", "mypy", "flake8"])

    mock_cli_run.assert_called_once_with(
        [f"{fake_project.joinpath('.venv').resolve()}"]
    )

    mock_install.assert_called_once_with(env, packages=["black", "mypy", "flake8"])
