"""
Tests for the conda module.

Author: Tom Fleet
Created: 20/06/2021
"""

import subprocess
from pathlib import Path
from typing import List, NamedTuple

import pytest
from pytest_mock import MockerFixture

from pytoil.environments import Conda
from pytoil.exceptions import (
    BadEnvironmentFileError,
    CondaNotInstalledError,
    EnvironmentAlreadyExistsError,
    EnvironmentDoesNotExistError,
    UnsupportedCondaInstallationError,
)


def test_conda_init():

    fake_project = Path("/Users/me/project/fakeproject")
    env = Conda(name="sillyenv", project_path=fake_project, conda="testconda")

    assert env.name == "sillyenv"
    assert env.project_path == fake_project.resolve()
    assert env.conda == "testconda"


def test_conda_init_conda_none():

    fake_project = Path("/Users/me/project/fakeproject")

    # You'd never manually set None but shutil.which will return None
    # if conda not on $PATH
    env = Conda(name="sillyenv", project_path=fake_project, conda=None)

    assert env.name == "sillyenv"
    assert env.project_path == fake_project.resolve()
    assert env.conda is None


def test_conda_repr():

    fake_project = Path("/Users/me/project/fakeproject")
    env = Conda(name="sillyenv", project_path=fake_project, conda="condaexe")

    expected = (
        f"Conda(name='sillyenv', project_path={env.project_path!r}, conda='condaexe')"
    )

    assert repr(env) == expected


def test_conda_info_name():

    fake_project = Path("/Users/me/project/fakeproject")
    env = Conda(name="test", project_path=fake_project, conda="testconda")

    assert env.info_name == "conda"


def test_raise_for_conda_raises_when_conda_not_installed():

    fake_project = Path("/Users/me/project/fakeproject")

    # Set conda to None to mimic what would happen if user
    # didn't have it installed
    env = Conda(name="sillyenv", project_path=fake_project, conda=None)

    with pytest.raises(CondaNotInstalledError):
        env.raise_for_conda()


def test_raise_for_conda_doesnt_raise_if_conda_installed():

    fake_project = Path("/Users/me/project/fakeproject")

    env = Conda(name="sillyenv", project_path=fake_project, conda="testconda")

    # Test will fail if this raises
    env.raise_for_conda()


def test_exists_returns_true_if_executable_exists(mocker: MockerFixture):

    fake_project = Path("/Users/me/project/fakeproject")

    mocker.patch(
        "pytoil.environments.conda.Path.exists",
        autospec=True,
        return_value=True,
    )

    mocker.patch(
        "pytoil.environments.conda.Conda.get_envs_dir",
        autospec=True,
        return_value=Path("/Users/me/miniconda3"),
    )

    env = Conda(name="test", project_path=fake_project, conda="testconda")

    assert env.exists() is True


def test_exists_returns_false_if_executable_doesnt_exist(
    mocker: MockerFixture,
):

    fake_project = Path("/Users/me/project/fakeproject")

    mocker.patch(
        "pytoil.environments.conda.Path.exists",
        autospec=True,
        return_value=False,
    )

    mocker.patch(
        "pytoil.environments.conda.Conda.get_envs_dir",
        autospec=True,
        return_value=Path("/Users/me/miniconda3"),
    )

    env = Conda(name="test", project_path=fake_project, conda="testconda")

    assert env.exists() is False


@pytest.mark.parametrize(
    "name, packages, expected_cmd",
    [
        (
            "sillyenv",
            ["black", "mypy", "flake8"],
            [
                "testconda",
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
                "testconda",
                "create",
                "-y",
                "--name",
                "dingleenv",
                "python=3",
            ],
        ),
    ],
)
def test_create_correctly_calls_subprocess(
    mocker: MockerFixture, name, packages, expected_cmd
):

    fake_project = Path("/Users/me/projects/fakeproject")

    mock_subprocess = mocker.patch(
        "pytoil.environments.conda.subprocess.run", autospec=True
    )

    # Give it a fake envs dir
    mocker.patch(
        "pytoil.environments.conda.Conda.get_envs_dir",
        autospec=True,
        return_value=Path("/Users/testyconda3/envs"),
    )

    env = Conda(name=name, project_path=fake_project, conda="testconda")

    env.create(packages=packages)

    mock_subprocess.assert_called_once_with(
        expected_cmd, check=True, capture_output=True
    )


def test_create_raises_if_already_exists(mocker: MockerFixture):

    fake_project = Path("/Users/me/projects/fakeproject")

    # Trick the test into thinking the environment already exists
    mocker.patch("pytoil.environments.Conda.exists", autospec=True, return_value=True)

    with pytest.raises(EnvironmentAlreadyExistsError):
        env = Conda(
            name="i_already_exist", project_path=fake_project, conda="testconda"
        )
        env.create()


def test_create_raises_on_subprocess_error(mocker: MockerFixture):

    fake_project = Path("/Users/me/projects/fakeproject")

    mocker.patch(
        "pytoil.environments.conda.subprocess.run",
        autospec=True,
        side_effect=[subprocess.CalledProcessError(-1, "cmd")],
    )

    # Give it a fake envs dir
    mocker.patch(
        "pytoil.environments.conda.Conda.get_envs_dir",
        autospec=True,
        return_value=Path("/Users/testyconda3/envs"),
    )

    with pytest.raises(subprocess.CalledProcessError):
        env = Conda(name="error", project_path=fake_project, conda="testconda")
        env.create()


def test_create_from_yml_correctly_calls_subprocess(
    mocker: MockerFixture, temp_environment_yml
):

    # Mock out the actual call to conda
    mock_subprocess = mocker.patch(
        "pytoil.environments.conda.subprocess.run", autospec=True
    )

    # Give it a fake envs dir
    mocker.patch(
        "pytoil.environments.conda.Conda.get_envs_dir",
        autospec=True,
        return_value=Path("/Users/testyconda3/envs"),
    )

    expected_cmd: List[str] = [
        "conda",
        "env",
        "create",
        "--file",
        f"{temp_environment_yml.resolve()}",
    ]

    env = Conda.create_from_yml(project_path=temp_environment_yml.parent)

    mock_subprocess.assert_called_once_with(
        expected_cmd, check=True, capture_output=True
    )

    # Assert the return is correct also
    assert env.name == "my_yml_env"
    assert env.project_path == temp_environment_yml.parent


def test_create_from_yml_raises_on_missing_file():

    fake_project = Path("/Users/me/projects/fakeproject")

    with pytest.raises(FileNotFoundError):
        Conda.create_from_yml(project_path=fake_project)


def test_create_from_yml_raises_on_invalid_formatted_yml(
    bad_temp_environment_yml, bad_temp_environment_yml_2
):

    with pytest.raises(BadEnvironmentFileError):
        Conda.create_from_yml(project_path=bad_temp_environment_yml.parent)

    with pytest.raises(BadEnvironmentFileError):
        Conda.create_from_yml(project_path=bad_temp_environment_yml_2.parent)


def test_create_from_yml_raises_if_env_already_exists(
    mocker: MockerFixture, temp_environment_yml
):

    mocker.patch("pytoil.environments.Conda.exists", autospec=True, return_value=True)

    with pytest.raises(EnvironmentAlreadyExistsError):
        Conda.create_from_yml(project_path=temp_environment_yml.parent)


def test_create_from_yml_raises_on_subprocess_error(
    mocker: MockerFixture, temp_environment_yml
):

    mocker.patch(
        "pytoil.environments.conda.subprocess.run",
        autospec=True,
        side_effect=[subprocess.CalledProcessError(-1, "cmd")],
    )

    # Give it a fake envs dir
    mocker.patch(
        "pytoil.environments.conda.Conda.get_envs_dir",
        autospec=True,
        return_value=Path("/Users/testyconda3/envs"),
    )

    with pytest.raises(subprocess.CalledProcessError):
        Conda.create_from_yml(project_path=temp_environment_yml.parent)


@pytest.mark.parametrize(
    "name, packages",
    [
        ("sillyenv", ["numpy", "pandas", "requests"]),
        ("dingleenv", ["black", "mypy", "dinglepython"]),
        ("blah", ["altair", "matplotlib", "seaborn"]),
    ],
)
def test_install_passes_correct_command(mocker: MockerFixture, name, packages):

    fake_project = Path("/Users/me/projects/fakeproject")

    mocker.patch("pytoil.environments.Conda.exists", autospec=True, return_value=True)

    mock_subprocess = mocker.patch(
        "pytoil.environments.conda.subprocess.run", autospec=True
    )

    expected_cmd: List[str] = [
        "testconda",
        "install",
        "-y",
        "--name",
        name,
    ]

    expected_cmd.extend(packages)

    env = Conda(name=name, project_path=fake_project, conda="testconda")

    env.install(packages=packages)

    mock_subprocess.assert_called_once_with(
        expected_cmd, check=True, capture_output=True
    )


def test_install_raises_if_environment_doesnt_exist(mocker: MockerFixture):

    fake_project = Path("/Users/me/projects/fakeproject")

    # Give it a fake envs dir
    mocker.patch(
        "pytoil.environments.conda.Conda.get_envs_dir",
        autospec=True,
        return_value=Path("/Users/testyconda3/envs"),
    )

    with pytest.raises(EnvironmentDoesNotExistError):
        env = Conda(name="missing", project_path=fake_project, conda="testconda")
        env.install(["black", "mypy", "pandas"])


def test_condaenv_install_raises_on_subprocess_error(mocker: MockerFixture):

    fake_project = Path("/Users/me/projects/fakeproject")

    mocker.patch("pytoil.environments.Conda.exists", autospec=True, return_value=True)

    mocker.patch(
        "pytoil.environments.conda.subprocess.run",
        autospec=True,
        side_effect=[subprocess.CalledProcessError(-1, "cmd")],
    )

    with pytest.raises(subprocess.CalledProcessError):
        env = Conda(name="error", project_path=fake_project, conda="testconda")
        env.install(["pandas", "numpy"])


def test_export_yml_raises_on_missing_env(mocker: MockerFixture):

    fake_project = Path("/Users/me/projects/fakeproject")

    mocker.patch("pytoil.environments.Conda.exists", autospec=True, return_value=False)

    mocker.patch("pytoil.environments.conda.subprocess.run", autospec=True)

    with pytest.raises(EnvironmentDoesNotExistError):
        env = Conda(name="condingle", project_path=fake_project, conda="testconda")
        env.export_yml()


def test_export_yml_raises_on_subprocess_error(mocker: MockerFixture):

    fake_project = Path("/Users/me/projects/fakeproject")

    mocker.patch("pytoil.environments.Conda.exists", autospec=True, return_value=True)

    mocker.patch(
        "pytoil.environments.conda.subprocess.run",
        autospec=True,
        side_effect=[subprocess.CalledProcessError(-1, "cmd")],
    )

    with pytest.raises(subprocess.CalledProcessError):
        env = Conda(name="blah", project_path=fake_project, conda="testconda")
        env.export_yml()


def test_condaenv_export_yml_exports_correct_content(
    mocker: MockerFixture, temp_environment_yml
):

    mocker.patch("pytoil.environments.Conda.exists", autospec=True, return_value=True)

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

    env = Conda(
        name="fake_conda_env",
        project_path=temp_environment_yml.parent,
        conda="testconda",
    )

    env.export_yml()

    assert temp_environment_yml.read_text(encoding="utf-8") == FakeStdOut().stdout

    mock_subprocess.assert_called_once_with(
        ["testconda", "env", "export", "--from-history", "--name", "fake_conda_env"],
        check=True,
        capture_output=True,
        encoding="utf-8",
    )


def test_get_envs_dir_returns_correctly_for_miniconda(
    mocker: MockerFixture, fake_home_folder_miniconda: Path
):

    mocker.patch(
        "pytoil.environments.conda.Path.home",
        autospec=True,
        return_value=fake_home_folder_miniconda,
    )

    env = Conda.get_envs_dir()

    expected_env_dir = fake_home_folder_miniconda.joinpath("miniconda3/envs")

    assert env == expected_env_dir


def test_get_envs_dir_returns_correctly_for_anaconda(
    mocker: MockerFixture, fake_home_folder_anaconda: Path
):

    mocker.patch(
        "pytoil.environments.conda.Path.home",
        autospec=True,
        return_value=fake_home_folder_anaconda,
    )

    env = Conda.get_envs_dir()

    expected_env_dir = fake_home_folder_anaconda.joinpath("anaconda3/envs")

    assert env == expected_env_dir


def test_get_envs_dir_returns_correctly_for_miniforge(
    mocker: MockerFixture, fake_home_folder_miniforge: Path
):

    mocker.patch(
        "pytoil.environments.conda.Path.home",
        autospec=True,
        return_value=fake_home_folder_miniforge,
    )

    env = Conda.get_envs_dir()

    expected_env_dir = fake_home_folder_miniforge.joinpath("miniforge3/envs")

    assert env == expected_env_dir


def test_get_envs_dir_returns_correctly_for_mambaforge(
    mocker: MockerFixture, fake_home_folder_mambaforge: Path
):

    mocker.patch(
        "pytoil.environments.conda.Path.home",
        autospec=True,
        return_value=fake_home_folder_mambaforge,
    )

    env = Conda.get_envs_dir()

    expected_env_dir = fake_home_folder_mambaforge.joinpath("mambaforge/envs")

    assert env == expected_env_dir


def test_get_envs_dir_raises_if_none_found(
    mocker: MockerFixture, fake_home_folder_no_conda: Path
):

    mocker.patch(
        "pytoil.environments.conda.Path.home",
        autospec=True,
        return_value=fake_home_folder_no_conda,
    )

    with pytest.raises(UnsupportedCondaInstallationError):
        Conda.get_envs_dir()


def test_install_self_calls_create_from_yml(mocker: MockerFixture):

    env = Conda(name="hello", project_path=Path("not/here"), conda="testconda")

    mock_create_from_yml = mocker.patch(
        "pytoil.environments.conda.Conda.create_from_yml", autospec=True
    )

    env.install_self()

    mock_create_from_yml.assert_called_once_with(project_path=env.project_path)
