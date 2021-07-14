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
from pytoil.exceptions import FlitNotInstalledError, MissingInterpreterError


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
    venv = FlitEnv(project_path=root)

    mocker.patch(
        "pytoil.environments.flit.Path.exists",
        autospec=True,
        return_value=pathlib_exists,
    )

    assert venv.exists() is pytoil_exists


def test_create_correctly_calls_venv_create(mocker: MockerFixture):

    root = Path("/Users/me/fakeproject")
    test_venv = FlitEnv(project_path=root)

    # Mock out the std lib venv create method
    mock_venv_create = mocker.patch(
        "pytoil.environments.flit.venv.create", autospec=True
    )

    # Also mock out our update seeds method so it doesn't do stuff
    mock_update_seeds = mocker.patch(
        "pytoil.environments.flit.FlitEnv.update_seeds", autospec=True
    )

    test_venv.create()

    # Should call std lib venv
    mock_venv_create.assert_called_once_with(
        env_dir=test_venv.project_path.joinpath(".venv"),
        clear=True,
        with_pip=True,
    )

    # And our update seeds method
    mock_update_seeds.assert_called_once()


def test_create_correctly_calls_venv_create_with_packages(mocker: MockerFixture):

    root = Path("/Users/me/fakeproject")
    test_venv = FlitEnv(project_path=root)

    # Mock out the std lib venv create method
    mock_venv_create = mocker.patch(
        "pytoil.environments.flit.venv.create", autospec=True
    )

    # Also mock out our update seeds method so it doesn't do stuff
    mock_update_seeds = mocker.patch(
        "pytoil.environments.flit.FlitEnv.update_seeds", autospec=True
    )

    # Now we're specifying packages, we need to mock out install
    # to avoid it actually doing stuff
    mock_install = mocker.patch(
        "pytoil.environments.flit.FlitEnv.install", autospec=True
    )

    test_venv.create(packages=["black", "requests", "flake8", "pandas"])

    # Should call std lib venv
    mock_venv_create.assert_called_once_with(
        env_dir=test_venv.project_path.joinpath(".venv"),
        clear=True,
        with_pip=True,
    )

    # And our update seeds method
    mock_update_seeds.assert_called_once()

    # Now make sure it's installing
    mock_install.assert_called_once_with(
        test_venv, packages=["black", "requests", "flake8", "pandas"]
    )


def test_update_seeds_raises_missing_interpreter_error():

    root = Path("/Users/somewhere/doesnt/exist")
    venv = FlitEnv(project_path=root)

    with pytest.raises(MissingInterpreterError):
        venv.update_seeds()


def test_update_seeds_passes_correct_command_to_subprocess(mocker: MockerFixture):

    root = Path("/Users/me/fakeproject")
    venv = FlitEnv(project_path=root)

    mock_subprocess = mocker.patch(
        "pytoil.environments.flit.subprocess.run", autospec=True
    )

    # Trick it into thinking the venv already exists so as not
    # to raise a MissingInterpreterError
    mocker.patch(
        "pytoil.environments.flit.FlitEnv.exists",
        autospec=True,
        return_value=True,
    )

    venv.update_seeds()

    mock_subprocess.assert_called_once_with(
        [
            f"{venv.executable}",
            "-m",
            "pip",
            "install",
            "--upgrade",
            "--quiet",
            "pip",
            "setuptools",
            "wheel",
        ],
        check=True,
    )


def test_update_seeds_raises_on_subprocess_error(mocker: MockerFixture):

    root = Path("/Users/me/fakeproject")
    venv = FlitEnv(project_path=root)

    mocker.patch(
        "pytoil.environments.flit.subprocess.run",
        autospec=True,
        side_effect=[subprocess.CalledProcessError(-1, "cmd")],
    )

    # Trick it into thinking the venv already exists so as not
    # to raise a MissingInterpreterError
    mocker.patch(
        "pytoil.environments.flit.FlitEnv.exists",
        autospec=True,
        return_value=True,
    )

    with pytest.raises(subprocess.CalledProcessError):
        venv.update_seeds()


def test_install_passes_correct_command_to_subprocess(mocker: MockerFixture):

    root = Path("/Users/me/fakeproject")
    venv = FlitEnv(project_path=root)

    mock_subprocess = mocker.patch(
        "pytoil.environments.flit.subprocess.run", autospec=True
    )

    # Trick it into thinking the venv already exists so as not
    # to raise a MissingInterpreterError
    mocker.patch(
        "pytoil.environments.flit.FlitEnv.exists",
        autospec=True,
        return_value=True,
    )

    venv.install(packages=["black", "flake8", "requests", "pandas>=1.0.0"])

    mock_subprocess.assert_called_once_with(
        [
            f"{venv.executable}",
            "-m",
            "pip",
            "install",
            "--quiet",
            "black",
            "flake8",
            "requests",
            "pandas>=1.0.0",
        ],
        check=True,
    )


def test_install_raises_on_subprocess_error(mocker: MockerFixture):

    root = Path("/Users/me/fakeproject")
    venv = FlitEnv(project_path=root)

    mocker.patch(
        "pytoil.environments.flit.subprocess.run",
        autospec=True,
        side_effect=[subprocess.CalledProcessError(-1, "cmd")],
    )

    # Trick it into thinking the venv already exists so as not
    # to raise a MissingInterpreterError
    mocker.patch(
        "pytoil.environments.flit.FlitEnv.exists",
        autospec=True,
        return_value=True,
    )

    with pytest.raises(subprocess.CalledProcessError):
        venv.install(["black", "mypy", "isort"])


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
