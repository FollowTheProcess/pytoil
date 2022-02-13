import asyncio
import shutil
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


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exists_return, want",
    [
        (True, True),
        (False, False),
    ],
)
async def test_exists(mocker: MockerFixture, exists_return: bool, want: bool):
    # Mock out aiofiles.os.path.exists to return what we want
    mocker.patch(
        "pytoil.environments.conda.aiofiles.os.path.exists",
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

    assert await conda.exists() is want


@pytest.mark.asyncio
async def test_create_raises_if_conda_not_installed():
    conda = Conda(root=Path("somewhere"), environment_name="test", conda=None)

    with pytest.raises(CondaNotInstalledError):
        await conda.create()


@pytest.mark.asyncio
async def test_create_raises_if_environment_already_exists(mocker: MockerFixture):
    conda = Conda(root=Path("somewhere"), environment_name="test", conda="notconda")

    # Make it think our "test" environment already exists
    mocker.patch(
        "pytoil.environments.conda.Conda.exists", autospec=True, return_value=True
    )

    with pytest.raises(EnvironmentAlreadyExistsError):
        await conda.create()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "packages, silent, stdout, stderr",
    [
        (
            ["black", "mypy", "isort"],
            True,
            asyncio.subprocess.DEVNULL,
            asyncio.subprocess.DEVNULL,
        ),
        (
            ["black", "mypy", "isort"],
            False,
            sys.stdout,
            sys.stderr,
        ),
    ],
)
async def test_create_correctly_adds_packages_if_specified(
    mocker: MockerFixture, packages: list[str], silent: bool, stdout, stderr
):
    conda = Conda(root=Path("somewhere"), environment_name="test", conda="notconda")

    mock_subprocess = mocker.patch(
        "pytoil.environments.conda.asyncio.create_subprocess_exec", autospec=True
    )

    # Mock the return of get_envs_dir so it thinks it exists regardless
    # of whether the tester has conda installed or not
    mocker.patch(
        "pytoil.environments.conda.Conda.get_envs_dir",
        autospec=True,
        return_value=Path("anaconda3/envs"),
    )

    await conda.create(packages=packages, silent=silent)

    mock_subprocess.assert_called_once_with(
        "notconda",
        "create",
        "-y",
        "--name",
        "test",
        "python=3",
        *packages,
        cwd=conda.project_path,
        stdout=stdout,
        stderr=stderr,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "silent, stdout, stderr",
    [
        (
            True,
            asyncio.subprocess.DEVNULL,
            asyncio.subprocess.DEVNULL,
        ),
        (
            False,
            sys.stdout,
            sys.stderr,
        ),
    ],
)
async def test_create_doesnt_add_packages_if_not_specified(
    mocker: MockerFixture, silent: bool, stdout, stderr
):
    conda = Conda(root=Path("somewhere"), environment_name="test", conda="notconda")

    mock_subprocess = mocker.patch(
        "pytoil.environments.conda.asyncio.create_subprocess_exec", autospec=True
    )

    # Mock the return of get_envs_dir so it thinks it exists regardless
    # of whether the tester has conda installed or not
    mocker.patch(
        "pytoil.environments.conda.Conda.get_envs_dir",
        autospec=True,
        return_value=Path("anaconda3/envs"),
    )

    await conda.create(silent=silent)

    mock_subprocess.assert_called_once_with(
        "notconda",
        "create",
        "-y",
        "--name",
        "test",
        "python=3",
        cwd=conda.project_path,
        stdout=stdout,
        stderr=stderr,
    )


@pytest.mark.asyncio
async def test_create_from_yml_raises_if_conda_not_installed(mocker: MockerFixture):
    conda = Conda(root=Path("somewhere"), environment_name="test")

    # Ensure shutil.which returns None
    mocker.patch(
        "pytoil.environments.conda.shutil.which",
        autospec=True,
        return_value=None,
    )

    with pytest.raises(CondaNotInstalledError):
        await conda.create_from_yml(Path("somewhere"), conda="notconda")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "silent, stdout, stderr",
    [
        (True, asyncio.subprocess.DEVNULL, asyncio.subprocess.DEVNULL),
        (False, sys.stdout, sys.stderr),
    ],
)
async def test_create_from_yml_correctly_calls_subprocess(
    mocker: MockerFixture, temp_environment_yml: Path, silent: bool, stdout, stderr
):

    # Mock out the actual call to conda
    mock_subprocess = mocker.patch(
        "pytoil.environments.conda.asyncio.create_subprocess_exec", autospec=True
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

    await conda.create_from_yml(
        project_path=temp_environment_yml.parent, conda="notconda", silent=silent
    )

    mock_subprocess.assert_called_once_with(
        "notconda",
        "env",
        "create",
        "--file",
        f"{temp_environment_yml.resolve()}",
        cwd=temp_environment_yml.resolve().parent,
        stdout=stdout,
        stderr=stderr,
    )


@pytest.mark.asyncio
async def test_create_from_yml_raises_on_bad_yml_file(
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
        await conda.create_from_yml(bad_temp_environment_yml.parent, conda="notconda")


@pytest.mark.asyncio
async def test_create_from_yml_raises_if_environment_already_exists(
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
        await conda.create_from_yml(
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


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "name, packages, silent, stdout, stderr",
    [
        (
            "sillyenv",
            ["numpy", "pandas", "requests"],
            True,
            asyncio.subprocess.DEVNULL,
            asyncio.subprocess.DEVNULL,
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
async def test_install_passes_correct_command(
    mocker: MockerFixture, name: str, packages: list[str], silent: bool, stdout, stderr
):

    fake_project = Path("/Users/me/projects/fakeproject")

    mocker.patch("pytoil.environments.Conda.exists", autospec=True, return_value=True)

    mock_subprocess = mocker.patch(
        "pytoil.environments.conda.asyncio.create_subprocess_exec", autospec=True
    )

    env = Conda(root=fake_project, environment_name="testy", conda="notconda")

    await env.install(packages=packages, silent=silent)

    mock_subprocess.assert_called_once_with(
        "notconda",
        "install",
        "-y",
        "--name",
        "testy",
        *packages,
        cwd=fake_project.resolve(),
        stdout=stdout,
        stderr=stderr,
    )


@pytest.mark.asyncio
async def test_install_raises_if_environment_doesnt_exist(mocker: MockerFixture):
    mocker.patch("pytoil.environments.Conda.exists", autospec=True, return_value=False)

    conda = Conda(root=Path("somewhere"), environment_name="testy", conda="notconda")

    with pytest.raises(EnvironmentDoesNotExistError):
        await conda.install(packages=["black", "mypy", "isort"])


@pytest.mark.asyncio
async def test_install_raises_if_conda_not_installed():

    conda = Conda(root=Path("somewhere"), environment_name="testy", conda=None)

    with pytest.raises(CondaNotInstalledError):
        await conda.install(packages=["black", "mypy", "isort"])


@pytest.mark.asyncio
@pytest.mark.parametrize("silent", [True, False])
async def test_install_self_calls_create_from_yml(mocker: MockerFixture, silent: bool):

    mock_create_from_yml = mocker.patch(
        "pytoil.environments.conda.Conda.create_from_yml", autospec=True
    )

    conda = Conda(root=Path("somewhere"), environment_name="testy", conda="notconda")

    await conda.install_self(silent=silent)

    mock_create_from_yml.assert_called_once_with(
        project_path=Path("somewhere").resolve(), silent=silent, conda="notconda"
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("silent", [True, False])
async def test_install_self_raises_if_conda_not_installed(
    mocker: MockerFixture, silent: bool
):
    mocker.patch("pytoil.environments.conda.Conda.create_from_yml", autospec=True)

    conda = Conda(root=Path("somewhere"), environment_name="testy", conda=None)

    with pytest.raises(CondaNotInstalledError):
        await conda.install_self(silent=silent)


@pytest.mark.asyncio
async def test_export_yml_raises_if_conda_not_installed():

    conda = Conda(root=Path("somewhere"), environment_name="testy", conda=None)

    with pytest.raises(CondaNotInstalledError):
        await conda.export_yml()


@pytest.mark.asyncio
async def test_export_yml_raises_on_missing_env(mocker: MockerFixture):

    mocker.patch(
        "pytoil.environments.conda.Conda.exists",
        autospec=True,
        return_value=False,
    )

    with pytest.raises(EnvironmentDoesNotExistError):
        env = Conda(root=Path("somewhere"), environment_name="testy", conda="notconda")
        await env.export_yml()


@pytest.mark.asyncio
async def test_export_yml(mocker: MockerFixture, temp_environment_yml: Path):
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

        async def communicate(self) -> tuple[bytes, bytes]:
            """
            Fake our stdout and stderr streams
            """
            return self.content.encode("utf-8"), self.content.encode("utf-8")

    mock_subprocess = mocker.patch(
        "pytoil.environments.conda.asyncio.create_subprocess_exec",
        autospec=True,
        return_value=Process(),
    )

    await conda.export_yml()

    mock_subprocess.assert_called_once_with(
        "notconda",
        "env",
        "export",
        "--from-history",
        "--name",
        "testy",
        cwd=temp_environment_yml.parent.resolve(),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    assert temp_environment_yml.read_text(encoding="utf-8") == Process().content
