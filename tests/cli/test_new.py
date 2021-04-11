"""
Tests for the pytoil new command.

Author: Tom Fleet
Created: 11/04/2021
"""

import pytest
from pytest_mock import MockerFixture
from typer.testing import CliRunner

from pytoil.cli.main import app
from pytoil.config import Config

runner = CliRunner()


def test_new_suggests_checkout_if_already_exists_local(
    mocker: MockerFixture, fake_projects_dir
):

    fake_config = Config(
        username="test",
        token="testtoken",
        projects_dir=fake_projects_dir,
        vscode=True,
    )

    mocker.patch(
        "pytoil.cli.main.Config.get",
        autospec=True,
        return_value=fake_config,
    )

    # Try to create one that is already in fake_projects_dir
    myproject_path = fake_projects_dir.joinpath("myproject")
    result = runner.invoke(app, ["new", "myproject"])
    assert result.exit_code == 1

    assert (
        f"Project: 'myproject' already exists locally at '{myproject_path}'."
        in result.stdout
    )

    assert "To resume an existing project, use 'checkout'." in result.stdout
    assert "Example: '$ pytoil checkout myproject'." in result.stdout
    assert "Aborted!" in result.stdout


def test_new_suggests_checkout_if_already_exists_remote(
    mocker: MockerFixture, fake_projects_dir
):

    fake_config = Config(
        username="test",
        token="testtoken",
        projects_dir=fake_projects_dir,
        vscode=True,
    )

    mocker.patch(
        "pytoil.cli.main.Config.get",
        autospec=True,
        return_value=fake_config,
    )

    # Whatever we try and create now, it will think it exists on GitHub
    mocker.patch("pytoil.cli.main.Repo.exists_remote", autospec=True, return_value=True)

    # Try to create one that is already in fake_projects_dir
    result = runner.invoke(app, ["new", "remote1"])
    assert result.exit_code == 1

    assert "Project: 'remote1' already exists on GitHub." in result.stdout

    assert "To resume an existing project, use 'checkout'." in result.stdout
    assert "Example: '$ pytoil checkout remote1'." in result.stdout
    assert "Aborted!" in result.stdout


@pytest.mark.parametrize(
    "cookie_option",
    ["--cookie", "-c"],
)
def test_new_with_cookiecutter_correctly_invokes_cookiecutter(
    mocker: MockerFixture, fake_projects_dir, cookie_option
):

    fake_config = Config(
        username="test",
        token="testtoken",
        projects_dir=fake_projects_dir,
        vscode=False,
    )

    mocker.patch(
        "pytoil.cli.main.Config.get",
        autospec=True,
        return_value=fake_config,
    )

    # Whatever we try and create now, it will think it doesn't already exist
    mocker.patch(
        "pytoil.cli.main.Repo.exists_remote", autospec=True, return_value=False
    )
    mocker.patch("pytoil.cli.main.Repo.exists_local", autospec=True, return_value=False)

    # Make sure it doesn't actually do anything
    mock_cookie = mocker.patch("pytoil.cli.main.cookiecutter", autospec=True)

    result = runner.invoke(
        app,
        [
            "new",
            "myproject",
            cookie_option,
            "https://github.com/some/cookie.git",
        ],
    )

    assert result.exit_code == 0

    assert (
        "Creating project: 'myproject' with cookiecutter template: "
        + "'https://github.com/some/cookie.git'."
        in result.stdout
    )

    mock_cookie.assert_called_once_with(
        template="https://github.com/some/cookie.git", output_dir=fake_projects_dir
    )


@pytest.mark.parametrize(
    "venv_option, venv_backend",
    [
        ("--venv", "virtualenv"),
        ("-v", "virtualenv"),
        ("--venv", "conda"),
        ("-v", "conda"),
    ],
)
def test_new_with_venv_correctly_creates_an_environment(
    mocker: MockerFixture,
    fake_projects_dir,
    venv_option,
    venv_backend,
):

    fake_config = Config(
        username="test",
        token="testtoken",
        projects_dir=fake_projects_dir,
        vscode=False,
    )

    mocker.patch(
        "pytoil.cli.main.Config.get",
        autospec=True,
        return_value=fake_config,
    )

    # Whatever we try and create now, it will think it doesn't already exist
    mocker.patch(
        "pytoil.cli.main.Repo.exists_remote", autospec=True, return_value=False
    )
    mocker.patch("pytoil.cli.main.Repo.exists_local", autospec=True, return_value=False)

    # Make it think we have a valid conda
    # And a valid virtualenv
    mocker.patch(
        "pytoil.cli.main.CondaEnv.exists",
        autospec=True,
        return_value=False,
    )

    mocker.patch(
        "pytoil.cli.main.VirtualEnv.exists",
        autospec=True,
        return_value=False,
    )

    # Make sure it doesn't actually do anything
    mock_virtualenv_create = mocker.patch(
        "pytoil.cli.main.VirtualEnv.create", autospec=True
    )
    mocker.patch("pytoil.cli.main.VirtualEnv.update_seeds", autospec=True)

    mock_conda_create = mocker.patch("pytoil.cli.main.CondaEnv.create", autospec=True)

    result = runner.invoke(
        app,
        [
            "new",
            "mynewproject",
            venv_option,
            venv_backend,
        ],
    )

    assert result.exit_code == 0

    if venv_backend == "virtualenv":
        assert "Creating virtualenv for 'mynewproject'." in result.stdout
        mock_virtualenv_create.assert_called_once()

    if venv_backend == "conda":
        assert "Creating conda environment for 'mynewproject'." in result.stdout
        mock_conda_create.assert_called_once()


def test_new_with_no_venv_doesnt_make_a_virtual_environment(
    mocker: MockerFixture, fake_projects_dir
):

    fake_config = Config(
        username="test",
        token="testtoken",
        projects_dir=fake_projects_dir,
        vscode=False,
    )

    mocker.patch(
        "pytoil.cli.main.Config.get",
        autospec=True,
        return_value=fake_config,
    )

    # Whatever we try and create now, it will think it doesn't already exist
    mocker.patch(
        "pytoil.cli.main.Repo.exists_remote", autospec=True, return_value=False
    )
    mocker.patch("pytoil.cli.main.Repo.exists_local", autospec=True, return_value=False)

    result = runner.invoke(app, ["new", "mynewproject"])
    assert result.exit_code == 0

    assert (
        "Virtual environment not requested. Skipping environment creation."
        in result.stdout
    )


def test_new_no_virtualenv_still_opens_code(mocker: MockerFixture, fake_projects_dir):

    fake_config = Config(
        username="test",
        token="testtoken",
        projects_dir=fake_projects_dir,
        vscode=True,
    )

    mocker.patch(
        "pytoil.cli.main.Config.get",
        autospec=True,
        return_value=fake_config,
    )

    # Whatever we try and create now, it will think it doesn't already exist
    mocker.patch(
        "pytoil.cli.main.Repo.exists_remote", autospec=True, return_value=False
    )
    mocker.patch("pytoil.cli.main.Repo.exists_local", autospec=True, return_value=False)

    mock_code_open = mocker.patch("pytoil.cli.main.VSCode.open", autospec=True)

    result = runner.invoke(app, ["new", "mynewproject"])

    assert result.exit_code == 0
    assert (
        "Virtual environment not requested. Skipping environment creation."
        in result.stdout
    )
    mock_code_open.assert_called_once()


@pytest.mark.parametrize("venv_option", ["--venv", "-v"])
def test_new_with_virtualenv_sets_pythonpath_and_opens_code(
    mocker: MockerFixture, fake_projects_dir, venv_option
):

    fake_config = Config(
        username="test",
        token="testtoken",
        projects_dir=fake_projects_dir,
        vscode=True,
    )

    mocker.patch(
        "pytoil.cli.main.Config.get",
        autospec=True,
        return_value=fake_config,
    )

    # Whatever we try and create now, it will think it doesn't already exist
    mocker.patch(
        "pytoil.cli.main.Repo.exists_remote", autospec=True, return_value=False
    )
    mocker.patch("pytoil.cli.main.Repo.exists_local", autospec=True, return_value=False)

    mocker.patch(
        "pytoil.cli.main.VirtualEnv.exists",
        autospec=True,
        return_value=False,
    )

    # Make sure it doesn't actually do anything
    mock_virtualenv_create = mocker.patch(
        "pytoil.cli.main.VirtualEnv.create", autospec=True
    )
    mocker.patch("pytoil.cli.main.VirtualEnv.update_seeds", autospec=True)

    mock_code_open = mocker.patch("pytoil.cli.main.VSCode.open", autospec=True)
    mock_code_ppath = mocker.patch(
        "pytoil.cli.main.VSCode.set_python_path", autospec=True
    )

    result = runner.invoke(app, ["new", "mynewproject", venv_option, "virtualenv"])

    assert result.exit_code == 0

    assert "Creating virtualenv for 'mynewproject'." in result.stdout

    mock_virtualenv_create.assert_called_once()

    assert "Setting 'python.pythonPath' in VSCode workspace." in result.stdout
    mock_code_ppath.assert_called_once()

    assert "Opening 'mynewproject' in VSCode..." in result.stdout
    mock_code_open.assert_called_once()


@pytest.mark.parametrize("venv_option", ["--venv", "-v"])
def test_new_with_conda_sets_pythonpath_and_opens_code(
    mocker: MockerFixture, fake_projects_dir, venv_option
):

    fake_config = Config(
        username="test",
        token="testtoken",
        projects_dir=fake_projects_dir,
        vscode=True,
    )

    mocker.patch(
        "pytoil.cli.main.Config.get",
        autospec=True,
        return_value=fake_config,
    )

    # Whatever we try and create now, it will think it doesn't already exist
    mocker.patch(
        "pytoil.cli.main.Repo.exists_remote", autospec=True, return_value=False
    )
    mocker.patch("pytoil.cli.main.Repo.exists_local", autospec=True, return_value=False)

    mocker.patch(
        "pytoil.cli.main.CondaEnv.exists",
        autospec=True,
        return_value=False,
    )

    mocker.patch(
        "pytoil.cli.main.CondaEnv.get_envs_dir",
        autospec=True,
        return_value=fake_projects_dir.parent.joinpath("miniconda3"),
    )

    # Make sure it doesn't actually do anything
    mock_conda_create = mocker.patch("pytoil.cli.main.CondaEnv.create", autospec=True)

    mock_code_open = mocker.patch("pytoil.cli.main.VSCode.open", autospec=True)
    mock_code_ppath = mocker.patch(
        "pytoil.cli.main.VSCode.set_python_path", autospec=True
    )

    result = runner.invoke(app, ["new", "mynewproject", venv_option, "conda"])

    assert result.exit_code == 0

    assert "Creating conda environment for 'mynewproject'." in result.stdout

    mock_conda_create.assert_called_once()

    assert "Setting 'python.pythonPath' in VSCode workspace." in result.stdout
    mock_code_ppath.assert_called_once()

    assert "Opening 'mynewproject' in VSCode..." in result.stdout
    mock_code_open.assert_called_once()
