"""
Tests for the virtualenv module.

Author: Tom Fleet
Created: 04/02/2021
"""

import pathlib
import subprocess

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

    assert env.basepath == pathlib.Path("made/up/dir").resolve()
    assert env.name == ".venv"  # Default name
    assert env.path == pathlib.Path("made/up/dir").joinpath(".venv").resolve()
    assert env.executable is None

    assert env2.basepath == pathlib.Path("made/up/dir").resolve()
    assert env2.name == "dinglevenv"  # Specified name
    assert env2.path == pathlib.Path("made/up/dir").joinpath("dinglevenv").resolve()
    assert env2.executable is None


def test_virtualenv_repr():

    path = pathlib.Path("made/up/dir")

    env = VirtualEnv(basepath=path)
    env2 = VirtualEnv(basepath=path, name="dinglevenv")

    assert env.__repr__() == f"VirtualEnv(basepath={path.resolve()!r}, name='.venv')"
    assert (
        env2.__repr__() == f"VirtualEnv(basepath={path.resolve()!r}, name='dinglevenv')"
    )


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
    mocker.patch("pytoil.env.virtualenv.cli_run", autospec=True)
    # Make it think the virtualenv does not already exist
    mocker.patch("pytoil.env.VirtualEnv.exists", autospec=True, return_value=False)

    # Make it think the basepath does exist
    mocker.patch(
        "pytoil.env.VirtualEnv.basepath_exists", autospec=True, return_value=True
    )

    # Create the virtualenv
    env.create()

    # Ensure the executable is correctly pathed and resolved
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


def test_virtualenv_update_seeds_raises_on_subprocess_error(mocker):

    # Patch out env.executable so raise_for_executable doesnt raise
    with mocker.patch.object(
        pytoil.env.VirtualEnv,
        "executable",
        pathlib.Path("made/up/dir/.venv/bin/python"),
    ):

        # Mock calling pip but have it raise
        mock_subprocess = mocker.patch(
            "pytoil.env.subprocess.run",
            autospec=True,
            side_effect=[subprocess.CalledProcessError(-1, "cmd")],
        )

        with pytest.raises(subprocess.CalledProcessError):
            env = VirtualEnv(basepath=pathlib.Path("made/up/dir"))
            env.update_seeds()

            # Assert pip would have been called with correct args
            mock_subprocess.assert_called_once_with(
                [
                    f"{str(env.executable)}",
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


# All conditions that should cause a raise
@pytest.mark.parametrize(
    "packages, prefix, requirements, editable",
    [
        (["black", "mypy", "madeup"], ".[dev]", "requirements.txt", True),
        (
            ["black", "mypy", "madeup"],
            ".[dev]",
            "requirements.txt",
            False,
        ),
        (["black", "mypy", "madeup"], ".[dev]", None, True),
        (["black", "mypy", "madeup"], ".[dev]", None, False),
        (["black", "mypy", "madeup"], None, None, True),
        (None, "[.dev]", "requirements.txt", True),
        (None, "[.dev]", "requirements.txt", False),
        (None, None, "requirements.txt", True),
        (None, None, None, True),
        (None, None, None, False),
    ],
)
def test_virtualenv_install_raises_on_mutually_exclusive_arguments(
    packages, prefix, requirements, editable
):

    env = VirtualEnv(basepath=pathlib.Path("made/up/dir"))

    with pytest.raises(ValueError):
        env.install(
            packages=packages,
            prefix=prefix,
            requirements=requirements,
            editable=editable,
        )


# Data for pip command construction
@pytest.mark.parametrize(
    "packages, prefix, requirements, editable, expected_cmd",
    [
        (
            ["black", "mypy", "madeup"],
            None,
            None,
            False,
            [
                f"{str(pathlib.Path('made/up/dir/.venv/bin/python').resolve())}",
                "-m",
                "pip",
                "install",
                "black",
                "mypy",
                "madeup",
            ],
        ),
        (
            None,
            ".[dev]",
            None,
            False,
            [
                f"{str(pathlib.Path('made/up/dir/.venv/bin/python').resolve())}",
                "-m",
                "pip",
                "install",
                ".[dev]",
            ],
        ),
        (
            None,
            ".[dev]",
            None,
            True,
            [
                f"{str(pathlib.Path('made/up/dir/.venv/bin/python').resolve())}",
                "-m",
                "pip",
                "install",
                "-e",
                ".[dev]",
            ],
        ),
        (
            None,
            None,
            "requirements.txt",
            False,
            [
                f"{str(pathlib.Path('made/up/dir/.venv/bin/python').resolve())}",
                "-m",
                "pip",
                "install",
                "-r",
                f"{str(pathlib.Path('made/up/dir/requirements.txt').resolve())}",
            ],
        ),
    ],
)
def test_virtualenv_install_passes_correct_command(
    mocker, packages, prefix, requirements, editable, expected_cmd
):
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
        pytoil.env.VirtualEnv,
        "executable",
        pathlib.Path("made/up/dir/.venv/bin/python").resolve(),
    ):
        # This doesnt actually matter, just has to be something
        env = VirtualEnv(basepath=pathlib.Path("made/up/dir"))

        # Mock the call to update_seeds contained within install
        mocker.patch(
            "pytoil.env.VirtualEnv.update_seeds", autospec=True, return_value=None
        )

        # Mock calling pip
        mock_subprocess = mocker.patch(
            "pytoil.env.subprocess.run",
            autospec=True,
        )

        # Call our install method with the parametrized arguments
        env.install(
            packages=packages,
            prefix=prefix,
            requirements=requirements,
            editable=editable,
        )

        # Assert pip would have been called with correct args
        mock_subprocess.assert_called_once_with(
            expected_cmd,
            check=True,
        )


@pytest.mark.parametrize(
    "packages, prefix, editable",
    [
        (
            ["black", "mypy", "madeup"],
            None,
            False,
        ),
        (
            None,
            ".[dev]",
            False,
        ),
        (
            None,
            ".[dev]",
            True,
        ),
    ],
)
def test_virtualenv_install_raises_on_subprocess_error(
    mocker, packages, prefix, editable
):
    """
    Done as a parametrized test so that we can be sure it raises regardless
    of what args passed so long as the args are valid.
    """

    # Force the executable property to be what we want so we can check output
    with mocker.patch.object(
        pytoil.env.VirtualEnv,
        "executable",
        pathlib.Path("made/up/dir/.venv/bin/python").resolve(),
    ):

        # Mock the call to update_seeds contained within install
        mocker.patch(
            "pytoil.env.VirtualEnv.update_seeds", autospec=True, return_value=None
        )

        # Mock calling pip, but have it raise
        mocker.patch(
            "pytoil.env.subprocess.run",
            autospec=True,
            side_effect=[subprocess.CalledProcessError(-1, "cmd")],
        )

        with pytest.raises(subprocess.CalledProcessError):
            # This doesnt actually matter, just has to be something
            env = VirtualEnv(basepath=pathlib.Path("made/up/dir"))

            env.install(packages=packages, prefix=prefix, editable=editable)
