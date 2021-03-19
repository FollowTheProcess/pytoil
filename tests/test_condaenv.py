"""
Tests for the CondaEnv management.

Author: Tom Fleet
Created: 10/02/2021
"""

import pathlib
import subprocess
from typing import List, NamedTuple

import pytest
from pytest_mock import MockerFixture

from pytoil.environments import CondaEnv
from pytoil.exceptions import (
    BadEnvironmentFileError,
    CondaNotInstalledError,
    UnknownCondaInstallationError,
    VirtualenvAlreadyExistsError,
    VirtualenvDoesNotExistError,
)


def test_condaenv_init():

    fake_project = pathlib.Path("/Users/me/project/fakeproject")

    env = CondaEnv(name="sillyenv", project_path=fake_project)

    assert env.name == "sillyenv"
    assert env.project_path == fake_project.resolve()


def test_condaenv_repr():

    fake_project = pathlib.Path("/Users/me/project/fakeproject")

    env = CondaEnv(name="sillyenv", project_path=fake_project)

    assert env.__repr__() == (
        f"CondaEnv(name='sillyenv', project_path={fake_project.resolve()!r})"
    )


def test_condaenv_raise_for_conda_raises_when_required(mocker: MockerFixture):

    fake_project = pathlib.Path("/Users/me/project/fakeproject")

    # Patch out shutil.which so it returns what we want it to
    mocker.patch(
        "pytoil.environments.conda.shutil.which", autospec=True, return_value=False
    )

    env = CondaEnv(name="sillyenv", project_path=fake_project)

    with pytest.raises(CondaNotInstalledError):
        env.raise_for_conda()


def test_condaenv_raise_for_conda_doesnt_raise_when_required(mocker: MockerFixture):

    fake_project = pathlib.Path("/Users/me/project/fakeproject")

    mocker.patch(
        "pytoil.environments.conda.shutil.which", autospec=True, return_value=True
    )

    env = CondaEnv(name="sillyenv", project_path=fake_project)

    # Test will fail if this raises
    env.raise_for_conda()


def test_condaenv_exists_returns_true_if_executable_exists(mocker: MockerFixture):

    fake_project = pathlib.Path("/Users/me/project/fakeproject")

    mocker.patch(
        "pytoil.environments.conda.pathlib.Path.exists",
        autospec=True,
        return_value=True,
    )

    mocker.patch(
        "pytoil.environments.conda.CondaEnv.get_envs_dir",
        autospec=True,
        return_value=pathlib.Path("/Users/me/miniconda3"),
    )

    env = CondaEnv(name="test", project_path=fake_project)

    assert env.exists() is True


def test_condaenv_exists_returns_false_if_executable_doesnt_exist(
    mocker: MockerFixture,
):

    fake_project = pathlib.Path("/Users/me/project/fakeproject")

    mocker.patch(
        "pytoil.environments.conda.pathlib.Path.exists",
        autospec=True,
        return_value=False,
    )

    mocker.patch(
        "pytoil.environments.conda.CondaEnv.get_envs_dir",
        autospec=True,
        return_value=pathlib.Path("/Users/me/miniconda3"),
    )

    env = CondaEnv(name="test", project_path=fake_project)

    assert env.exists() is False


@pytest.mark.parametrize(
    "name, packages, expected_cmd",
    [
        (
            "sillyenv",
            ["black", "mypy", "flake8"],
            [
                "conda",
                "create",
                "-y",
                "--name",
                "sillyenv",
                "python=3",
                "black",
                "mypy",
                "flake8",
            ],
        ),
        (
            "dingleenv",
            None,
            [
                "conda",
                "create",
                "-y",
                "--name",
                "dingleenv",
                "python=3",
            ],
        ),
    ],
)
def test_condaenv_create_is_correctly_called(
    mocker: MockerFixture, name, packages, expected_cmd
):

    fake_project = pathlib.Path("/Users/me/projects/fakeproject")

    # Trick the test into thinking the environment doesn't already exist
    mocker.patch(
        "pytoil.environments.CondaEnv.exists", autospec=True, return_value=False
    )

    mock_subprocess = mocker.patch(
        "pytoil.environments.conda.subprocess.run", autospec=True
    )

    env = CondaEnv(name=name, project_path=fake_project)

    env.create(packages=packages)

    mock_subprocess.assert_called_once_with(expected_cmd, check=True)


def test_condaenv_create_raises_if_already_exists(mocker: MockerFixture):

    fake_project = pathlib.Path("/Users/me/projects/fakeproject")

    # Trick the test into thinking the environment already exists
    mocker.patch(
        "pytoil.environments.CondaEnv.exists", autospec=True, return_value=True
    )

    with pytest.raises(VirtualenvAlreadyExistsError):
        env = CondaEnv(name="i_already_exist", project_path=fake_project)
        env.create()


def test_condaenv_create_raises_on_subprocess_error(mocker: MockerFixture):

    fake_project = pathlib.Path("/Users/me/projects/fakeproject")

    mocker.patch(
        "pytoil.environments.CondaEnv.exists", autospec=True, return_value=False
    )

    mocker.patch(
        "pytoil.environments.conda.subprocess.run",
        autospec=True,
        side_effect=[subprocess.CalledProcessError(-1, "cmd")],
    )

    with pytest.raises(subprocess.CalledProcessError):
        env = CondaEnv(name="error", project_path=fake_project)
        env.create()


def test_condaenv_create_from_yml_passes_correct_command(
    mocker: MockerFixture, temp_environment_yml
):

    # Make it think the environment doesn't already exist
    mocker.patch(
        "pytoil.environments.CondaEnv.exists", autospec=True, return_value=False
    )

    # Mock out the actual call to conda
    mock_subprocess = mocker.patch(
        "pytoil.environments.conda.subprocess.run", autospec=True
    )

    expected_cmd: List[str] = [
        "conda",
        "env",
        "create",
        "-y",
        "--file",
        f"{temp_environment_yml.resolve()}",
    ]

    env = CondaEnv.create_from_yml(project_path=temp_environment_yml.parent)

    mock_subprocess.assert_called_once_with(expected_cmd, check=True)

    # Assert the return is correct also
    assert env.name == "my_yml_env"
    assert env.project_path == temp_environment_yml.parent


def test_condaenv_create_from_yml_raises_on_missing_file(mocker: MockerFixture):

    fake_project = pathlib.Path("/Users/me/projects/fakeproject")

    mocker.patch(
        "pytoil.environments.CondaEnv.exists", autospec=True, return_value=False
    )

    with pytest.raises(FileNotFoundError):
        CondaEnv.create_from_yml(project_path=fake_project)


def test_condaenv_create_from_yml_raises_on_invalid_formatted_yml(
    mocker: MockerFixture, bad_temp_environment_yml, bad_temp_environment_yml_2
):

    mocker.patch(
        "pytoil.environments.CondaEnv.exists", autospec=True, return_value=False
    )

    with pytest.raises(BadEnvironmentFileError):
        CondaEnv.create_from_yml(project_path=bad_temp_environment_yml.parent)

    with pytest.raises(BadEnvironmentFileError):
        CondaEnv.create_from_yml(project_path=bad_temp_environment_yml_2.parent)


def test_condaenv_create_from_yml_raises_if_env_already_exists(
    mocker: MockerFixture, temp_environment_yml
):

    mocker.patch(
        "pytoil.environments.CondaEnv.exists", autospec=True, return_value=True
    )

    with pytest.raises(VirtualenvAlreadyExistsError):
        CondaEnv.create_from_yml(project_path=temp_environment_yml.parent)


def test_condaenv_create_from_yml_raises_on_subprocess_error(
    mocker: MockerFixture, temp_environment_yml
):

    mocker.patch(
        "pytoil.environments.CondaEnv.exists", autospec=True, return_value=False
    )

    mocker.patch(
        "pytoil.environments.conda.subprocess.run",
        autospec=True,
        side_effect=[subprocess.CalledProcessError(-1, "cmd")],
    )

    with pytest.raises(subprocess.CalledProcessError):
        CondaEnv.create_from_yml(project_path=temp_environment_yml.parent)


@pytest.mark.parametrize(
    "name, packages",
    [
        ("sillyenv", ["numpy", "pandas", "requests"]),
        ("dingleenv", ["black", "mypy", "dinglepython"]),
        ("blah", ["altair", "matplotlib", "seaborn"]),
    ],
)
def test_condaenv_install_passes_correct_command(mocker: MockerFixture, name, packages):

    fake_project = pathlib.Path("/Users/me/projects/fakeproject")

    mocker.patch(
        "pytoil.environments.CondaEnv.exists", autospec=True, return_value=True
    )

    mock_subprocess = mocker.patch(
        "pytoil.environments.conda.subprocess.run", autospec=True
    )

    expected_cmd: List[str] = [
        "conda",
        "install",
        "--name",
        name,
        "-y",
    ]

    expected_cmd.extend(packages)

    env = CondaEnv(name=name, project_path=fake_project)

    env.install(packages=packages)

    mock_subprocess.assert_called_once_with(expected_cmd, check=True)


def test_condaenv_install_raises_if_environment_doesnt_exist(mocker: MockerFixture):

    fake_project = pathlib.Path("/Users/me/projects/fakeproject")

    mocker.patch(
        "pytoil.environments.CondaEnv.exists", autospec=True, return_value=False
    )

    with pytest.raises(VirtualenvDoesNotExistError):
        env = CondaEnv(name="missing", project_path=fake_project)
        env.install(["black", "mypy", "pandas"])


def test_condaenv_install_raises_on_subprocess_error(mocker: MockerFixture):

    fake_project = pathlib.Path("/Users/me/projects/fakeproject")

    mocker.patch(
        "pytoil.environments.CondaEnv.exists", autospec=True, return_value=True
    )

    mocker.patch(
        "pytoil.environments.conda.subprocess.run",
        autospec=True,
        side_effect=[subprocess.CalledProcessError(-1, "cmd")],
    )

    with pytest.raises(subprocess.CalledProcessError):
        env = CondaEnv(name="error", project_path=fake_project)
        env.install(["pandas", "numpy"])


def test_condaenv_export_yml_raises_on_missing_env(mocker: MockerFixture):

    fake_project = pathlib.Path("/Users/me/projects/fakeproject")

    mocker.patch(
        "pytoil.environments.CondaEnv.exists", autospec=True, return_value=False
    )

    mocker.patch("pytoil.environments.conda.subprocess.run", autospec=True)

    with pytest.raises(VirtualenvDoesNotExistError):
        env = CondaEnv(name="condingle", project_path=fake_project)
        env.export_yml()


def test_condaenv_export_yml_raises_on_subprocess_error(mocker: MockerFixture):

    fake_project = pathlib.Path("/Users/me/projects/fakeproject")

    mocker.patch(
        "pytoil.environments.CondaEnv.exists", autospec=True, return_value=True
    )

    mocker.patch(
        "pytoil.environments.conda.subprocess.run",
        autospec=True,
        side_effect=[subprocess.CalledProcessError(-1, "cmd")],
    )

    with pytest.raises(subprocess.CalledProcessError):
        env = CondaEnv(name="blah", project_path=fake_project)
        env.export_yml()


def test_condaenv_export_yml_exports_correct_content(
    mocker: MockerFixture, temp_environment_yml
):

    mocker.patch(
        "pytoil.environments.CondaEnv.exists", autospec=True, return_value=True
    )

    class FakeStdOut(NamedTuple):
        # we need this so the returned object from subprocess.run
        # has a `.stdout` attribute
        stdout: str = """
        name: fake_conda_env
        channels:
        - defaults
        - conda-forge
        dependencies:
        - python=3
        - invoke
        - black
        - flake8
        - isort
        - mypy
        - rich
        - numpy
        - requests
        - pandas
        - matplotlib
        - seaborn
        - altair
        - altair_data_server
        - altair_saver
        - ipykernel
        - jupyterlab
        - sqlalchemy
        - pandas-profiling
        - hiplot
        """

    mock_subprocess = mocker.patch(
        "pytoil.environments.conda.subprocess.run",
        autospec=True,
        return_value=FakeStdOut(),
    )

    env = CondaEnv(name="fake_conda_env", project_path=temp_environment_yml.parent)

    env.export_yml()

    assert temp_environment_yml.read_text(encoding="utf-8") == FakeStdOut().stdout

    mock_subprocess.assert_called_once_with(
        ["conda", "env", "export", "--from-history", "--name", "fake_conda_env"],
        check=True,
        capture_output=True,
        encoding="utf-8",
    )


def test_condaenv_get_envs_dir_returns_correctly_for_miniconda(
    mocker: MockerFixture, fake_home_folder_miniconda: pathlib.Path
):

    mocker.patch(
        "pytoil.environments.conda.pathlib.Path.home",
        autospec=True,
        return_value=fake_home_folder_miniconda,
    )

    env = CondaEnv.get_envs_dir()

    expected_env_dir = fake_home_folder_miniconda.joinpath("miniconda3/envs")

    assert env == expected_env_dir


def test_condaenv_get_envs_dir_returns_correctly_for_anaconda(
    mocker: MockerFixture, fake_home_folder_anaconda: pathlib.Path
):

    mocker.patch(
        "pytoil.environments.conda.pathlib.Path.home",
        autospec=True,
        return_value=fake_home_folder_anaconda,
    )

    env = CondaEnv.get_envs_dir()

    expected_env_dir = fake_home_folder_anaconda.joinpath("anaconda3/envs")

    assert env == expected_env_dir


def test_condaenv_get_envs_dir_raises_if_neither_found(
    mocker: MockerFixture, fake_home_folder_neither: pathlib.Path
):

    mocker.patch(
        "pytoil.environments.conda.pathlib.Path.home",
        autospec=True,
        return_value=fake_home_folder_neither,
    )

    with pytest.raises(UnknownCondaInstallationError):
        CondaEnv.get_envs_dir()
