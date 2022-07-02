from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple

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


def test_conda_default(mocker: MockerFixture):
    conda = Conda(root=Path("somewhere"), environment_name="test")

    # Mock the return of get_envs_dir so it thinks it exists regardless
    # of whether the tester has conda installed or not
    mocker.patch(
        "pytoil.environments.conda.Conda.get_envs_dir",
        autospec=True,
        return_value=Path("anaconda3/envs"),
    )

    assert conda.project_path == Path("somewhere").resolve()
    assert conda.executable == Path("anaconda3/envs").joinpath("test/bin/python")
    assert conda.name == "conda"
    assert conda.environment_name == "test"
    assert conda.conda == shutil.which("conda")


def test_conda_passed(mocker: MockerFixture):
    conda = Conda(root=Path("somewhere"), environment_name="test", conda="notconda")

    # Mock the return of get_envs_dir so it thinks it exists regardless
    # of whether the tester has conda installed or not
    mocker.patch(
        "pytoil.environments.conda.Conda.get_envs_dir",
        autospec=True,
        return_value=Path("anaconda3/envs"),
    )

    assert conda.project_path == Path("somewhere").resolve()
    assert conda.executable == Path("anaconda3/envs").joinpath("test/bin/python")
    assert conda.name == "conda"
    assert conda.environment_name == "test"
    assert conda.conda == "notconda"


def test_conda_repr():
    conda = Conda(root=Path("somewhere"), environment_name="test", conda="notconda")
    assert (
        repr(conda)
        == f"Conda(root={Path('somewhere')!r}, environment_name='test',"
        " conda='notconda')"
    )


@pytest.mark.parametrize(
    "exists_return, want",
    [
        (True, True),
        (False, False),
    ],
)
def test_exists(mocker: MockerFixture, exists_return: bool, want: bool):
    mocker.patch(
        "pytoil.environments.conda.Path.exists",
        autospec=True,
        return_value=exists_return,
    )

    # Mock the return of get_envs_dir so it thinks it exists regardless
    # of whether the tester has conda installed or not
    mocker.patch(
        "pytoil.environments.conda.Conda.get_envs_dir",
        autospec=True,
        return_value=Path("anaconda3/envs"),
    )

    conda = Conda(root=Path("somewhere"), environment_name="test", conda="notconda")

    assert conda.exists() is want


def test_create_raises_if_conda_not_installed():
    conda = Conda(root=Path("somewhere"), environment_name="test", conda=None)

    with pytest.raises(CondaNotInstalledError):
        conda.create()


def test_create_raises_if_environment_already_exists(mocker: MockerFixture):
    conda = Conda(root=Path("somewhere"), environment_name="test", conda="notconda")

    # Make it think our "test" environment already exists
    mocker.patch(
        "pytoil.environments.conda.Conda.exists", autospec=True, return_value=True
    )

    with pytest.raises(EnvironmentAlreadyExistsError):
        conda.create()


@pytest.mark.parametrize(
    "packages, silent, stdout, stderr",
    [
        (
            ["black", "mypy", "isort"],
            True,
            subprocess.DEVNULL,
            subprocess.DEVNULL,
        ),
        (
            ["black", "mypy", "isort"],
            False,
            sys.stdout,
            sys.stderr,
        ),
    ],
)
def test_create_correctly_adds_packages_if_specified(
    mocker: MockerFixture, packages: list[str], silent: bool, stdout, stderr
):
    conda = Conda(root=Path("somewhere"), environment_name="test", conda="notconda")

    mock_subprocess = mocker.patch(
        "pytoil.environments.conda.subprocess.run", autospec=True
    )

    # Mock the return of get_envs_dir so it thinks it exists regardless
    # of whether the tester has conda installed or not
    mocker.patch(
        "pytoil.environments.conda.Conda.get_envs_dir",
        autospec=True,
        return_value=Path("anaconda3/envs"),
    )

    conda.create(packages=packages, silent=silent)

    mock_subprocess.assert_called_once_with(
        ["notconda", "create", "-y", "--name", "test", "python=3", *packages],
        cwd=conda.project_path,
        stdout=stdout,
        stderr=stderr,
    )


@pytest.mark.parametrize(
    "silent, stdout, stderr",
    [
        (
            True,
            subprocess.DEVNULL,
            subprocess.DEVNULL,
        ),
        (
            False,
            sys.stdout,
            sys.stderr,
        ),
    ],
)
def test_create_doesnt_add_packages_if_not_specified(
    mocker: MockerFixture, silent: bool, stdout, stderr
):
    conda = Conda(root=Path("somewhere"), environment_name="test", conda="notconda")

    mock_subprocess = mocker.patch(
        "pytoil.environments.conda.subprocess.run", autospec=True
    )

    # Mock the return of get_envs_dir so it thinks it exists regardless
    # of whether the tester has conda installed or not
    mocker.patch(
        "pytoil.environments.conda.Conda.get_envs_dir",
        autospec=True,
        return_value=Path("anaconda3/envs"),
    )

    conda.create(silent=silent)

    mock_subprocess.assert_called_once_with(
        ["notconda", "create", "-y", "--name", "test", "python=3"],
        cwd=conda.project_path,
        stdout=stdout,
        stderr=stderr,
    )


def test_create_from_yml_raises_if_conda_not_installed(mocker: MockerFixture):
    conda = Conda(root=Path("somewhere"), environment_name="test")

    # Ensure shutil.which returns None
    mocker.patch(
        "pytoil.environments.conda.shutil.which",
        autospec=True,
        return_value=None,
    )

    with pytest.raises(CondaNotInstalledError):
        conda.create_from_yml(Path("somewhere"), conda="notconda")


@pytest.mark.parametrize(
    "silent, stdout, stderr",
    [
        (True, subprocess.DEVNULL, subprocess.DEVNULL),
        (False, sys.stdout, sys.stderr),
    ],
)
def test_create_from_yml_correctly_calls_subprocess(
    mocker: MockerFixture, temp_environment_yml: Path, silent: bool, stdout, stderr
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

    # Ensure shutil.which doesn't fail
    mocker.patch(
        "pytoil.environments.conda.shutil.which",
        autospec=True,
        return_value="conda",
    )

    conda = Conda(root=Path("somewhere"), environment_name="test", conda="notconda")

    conda.create_from_yml(
        project_path=temp_environment_yml.parent, conda="notconda", silent=silent
    )

    mock_subprocess.assert_called_once_with(
        ["notconda", "env", "create", "--file", f"{temp_environment_yml.resolve()}"],
        cwd=temp_environment_yml.resolve().parent,
        stdout=stdout,
        stderr=stderr,
    )


def test_create_from_yml_raises_on_bad_yml_file(
    mocker: MockerFixture, bad_temp_environment_yml: Path
):
    # Ensure shutil.which doesn't fail
    mocker.patch(
        "pytoil.environments.conda.shutil.which",
        autospec=True,
        return_value="notconda",
    )

    conda = Conda(root=Path("somewhere"), environment_name="test", conda="notconda")

    with pytest.raises(BadEnvironmentFileError):
        conda.create_from_yml(bad_temp_environment_yml.parent, conda="notconda")


def test_create_from_yml_raises_if_environment_already_exists(
    mocker: MockerFixture, temp_environment_yml: Path
):
    # Ensure shutil.which doesn't fail
    mocker.patch(
        "pytoil.environments.conda.shutil.which",
        autospec=True,
        return_value="notconda",
    )

    # Make it think the environment already exists
    mocker.patch(
        "pytoil.environments.conda.Conda.exists", autospec=True, return_value=True
    )

    conda = Conda(root=Path("somewhere"), environment_name="test", conda="notconda")

    with pytest.raises(EnvironmentAlreadyExistsError):
        conda.create_from_yml(
            project_path=temp_environment_yml.parent, conda="notconda"
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


@pytest.mark.parametrize(
    "name, packages, silent, stdout, stderr",
    [
        (
            "sillyenv",
            ["numpy", "pandas", "requests"],
            True,
            subprocess.DEVNULL,
            subprocess.DEVNULL,
        ),
        (
            "sillyenv",
            ["numpy", "pandas", "requests"],
            False,
            sys.stdout,
            sys.stderr,
        ),
    ],
)
def test_install_passes_correct_command(
    mocker: MockerFixture, name: str, packages: list[str], silent: bool, stdout, stderr
):
    fake_project = Path("/Users/me/projects/fakeproject")

    mocker.patch("pytoil.environments.Conda.exists", autospec=True, return_value=True)

    mock_subprocess = mocker.patch(
        "pytoil.environments.conda.subprocess.run", autospec=True
    )

    env = Conda(root=fake_project, environment_name="testy", conda="notconda")

    env.install(packages=packages, silent=silent)

    mock_subprocess.assert_called_once_with(
        ["notconda", "install", "-y", "--name", "testy", *packages],
        cwd=fake_project.resolve(),
        stdout=stdout,
        stderr=stderr,
    )


def test_install_raises_if_environment_doesnt_exist(mocker: MockerFixture):
    mocker.patch("pytoil.environments.Conda.exists", autospec=True, return_value=False)

    conda = Conda(root=Path("somewhere"), environment_name="testy", conda="notconda")

    with pytest.raises(EnvironmentDoesNotExistError):
        conda.install(packages=["black", "mypy", "isort"])


def test_install_raises_if_conda_not_installed():
    conda = Conda(root=Path("somewhere"), environment_name="testy", conda=None)

    with pytest.raises(CondaNotInstalledError):
        conda.install(packages=["black", "mypy", "isort"])


@pytest.mark.parametrize("silent", [True, False])
def test_install_self_calls_create_from_yml(mocker: MockerFixture, silent: bool):
    mock_create_from_yml = mocker.patch(
        "pytoil.environments.conda.Conda.create_from_yml", autospec=True
    )

    conda = Conda(root=Path("somewhere"), environment_name="testy", conda="notconda")

    conda.install_self(silent=silent)

    mock_create_from_yml.assert_called_once_with(
        project_path=Path("somewhere").resolve(), silent=silent, conda="notconda"
    )


@pytest.mark.parametrize("silent", [True, False])
def test_install_self_raises_if_conda_not_installed(
    mocker: MockerFixture, silent: bool
):
    mocker.patch("pytoil.environments.conda.Conda.create_from_yml", autospec=True)

    conda = Conda(root=Path("somewhere"), environment_name="testy", conda=None)

    with pytest.raises(CondaNotInstalledError):
        conda.install_self(silent=silent)


def test_export_yml_raises_if_conda_not_installed():
    conda = Conda(root=Path("somewhere"), environment_name="testy", conda=None)

    with pytest.raises(CondaNotInstalledError):
        conda.export_yml()


def test_export_yml_raises_on_missing_env(mocker: MockerFixture):
    mocker.patch(
        "pytoil.environments.conda.Conda.exists",
        autospec=True,
        return_value=False,
    )

    with pytest.raises(EnvironmentDoesNotExistError):
        env = Conda(root=Path("somewhere"), environment_name="testy", conda="notconda")
        env.export_yml()


def test_export_yml(mocker: MockerFixture, temp_environment_yml: Path):
    # It must think the environment exists
    mocker.patch(
        "pytoil.environments.conda.Conda.exists",
        autospec=True,
        return_value=True,
    )

    conda = Conda(
        root=temp_environment_yml.parent, environment_name="testy", conda="notconda"
    )

    class Process(NamedTuple):
        content: str = """
        name: testy
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
        """

        @property
        def stdout(self) -> str:
            return self.content

    mock_subprocess = mocker.patch(
        "pytoil.environments.conda.subprocess.run",
        autospec=True,
        return_value=Process(),
    )

    conda.export_yml()

    mock_subprocess.assert_called_once_with(
        ["notconda", "env", "export", "--from-history", "--name", "testy"],
        cwd=temp_environment_yml.parent.resolve(),
        capture_output=True,
        encoding="utf-8",
    )

    assert temp_environment_yml.read_text(encoding="utf-8") == Process().content
