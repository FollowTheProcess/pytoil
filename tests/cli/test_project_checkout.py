"""
Tests for the project checkout CLI command.

Author: Tom Fleet
Created: 11/03/2021
"""

import pathlib

from pytest_mock import MockerFixture
from typer.testing import CliRunner

from pytoil.cli.main import app
from pytoil.config import Config
from pytoil.environments import CondaEnv, VirtualEnv

runner = CliRunner()


def test_checkout_aborts_if_no_matches_found(mocker: MockerFixture, fake_projects_dir):

    fake_config = Config(
        username="test",
        token="testtoken",
        projects_dir=fake_projects_dir,
        vscode=True,
    )

    mocker.patch(
        "pytoil.cli.project.Config.get",
        autospec=True,
        return_value=fake_config,
    )

    # Make it think it doesn't exist locally or remotely
    mocker.patch(
        "pytoil.cli.project.Repo.exists_local", autospec=True, return_value=False
    )
    mocker.patch(
        "pytoil.cli.project.Repo.exists_remote", autospec=True, return_value=False
    )

    # Try to checkout a project

    result = runner.invoke(app, ["project", "checkout", "not_here"])
    assert result.exit_code == 1
    assert "Project: 'not_here' not found locally or on your GitHub" in result.stdout
    assert "Does the project exist?" in result.stdout
    assert (
        "If not, create a new project: '$ pytoil project create not_here'."
        in result.stdout
    )


def test_checkout_correctly_identifies_local_project(
    mocker: MockerFixture, fake_projects_dir
):

    fake_config = Config(
        username="test",
        token="testtoken",
        projects_dir=fake_projects_dir,
        vscode=False,  # So we don't try and open anything
    )

    mocker.patch(
        "pytoil.cli.project.Config.get",
        autospec=True,
        return_value=fake_config,
    )

    # Whatever we try and checkout will proceed as if it's local
    mocker.patch(
        "pytoil.cli.project.Repo.exists_local", autospec=True, return_value=True
    )

    local_project_path: pathlib.Path = fake_projects_dir.joinpath("local1")

    result = runner.invoke(app, ["project", "checkout", "local1"])
    assert result.exit_code == 0
    assert (
        f"Project: 'local1' is available locally at '{local_project_path}'."
        in result.stdout
    )


def test_checkout_correctly_identifies_remote_project(
    mocker: MockerFixture, fake_projects_dir
):

    fake_config = Config(
        username="test",
        token="testtoken",
        projects_dir=fake_projects_dir,
        vscode=False,  # So we don't try and open anything
    )

    mocker.patch(
        "pytoil.cli.project.Config.get",
        autospec=True,
        return_value=fake_config,
    )

    # Whatever we try and checkout will proceeed as if its remote only
    mocker.patch(
        "pytoil.cli.project.Repo.exists_local", autospec=True, return_value=False
    )

    mocker.patch(
        "pytoil.cli.project.Repo.exists_remote", autospec=True, return_value=True
    )

    # So we don't actually try and clone anything
    mock_clone = mocker.patch("pytoil.cli.project.Repo.clone", autospec=True)

    # So we don't try and create a virtual environment
    mock_env_dispatcher = mocker.patch(
        "pytoil.cli.project.env_dispatcher", autospec=True, return_value=None
    )

    result = runner.invoke(app, ["project", "checkout", "remote1"])
    assert result.exit_code == 0
    assert "Project: 'remote1' found on your GitHub. Cloning..." in result.stdout
    mock_clone.assert_called_once()
    mock_env_dispatcher.assert_called_once()
    assert "Unable to auto-detect virtual environment. Skipping." in result.stdout


def test_checkout_local_correctly_opens_vscode_if_configured(
    mocker: MockerFixture, fake_projects_dir
):

    fake_config = Config(
        username="test",
        token="testtoken",
        projects_dir=fake_projects_dir,
        vscode=True,
    )

    mocker.patch(
        "pytoil.cli.project.Config.get",
        autospec=True,
        return_value=fake_config,
    )

    mocker.patch(
        "pytoil.cli.project.Repo.exists_local", autospec=True, return_value=True
    )

    # So we don't actually open code
    mock_code_open = mocker.patch("pytoil.cli.project.VSCode.open", autospec=True)

    local_project_path: pathlib.Path = fake_projects_dir.joinpath("local1")

    result = runner.invoke(app, ["project", "checkout", "local1"])
    assert result.exit_code == 0

    assert (
        f"Project: 'local1' is available locally at '{local_project_path}'."
        in result.stdout
    )
    assert "Opening 'local1' in VSCode..." in result.stdout

    mock_code_open.assert_called_once()


def test_checkout_remote_correctly_opens_vscode_if_configured(
    mocker: MockerFixture, fake_projects_dir
):

    fake_config = Config(
        username="test",
        token="testtoken",
        projects_dir=fake_projects_dir,
        vscode=True,
    )

    mocker.patch(
        "pytoil.cli.project.Config.get",
        autospec=True,
        return_value=fake_config,
    )

    mocker.patch(
        "pytoil.cli.project.Repo.exists_local", autospec=True, return_value=False
    )

    mocker.patch(
        "pytoil.cli.project.Repo.exists_remote", autospec=True, return_value=True
    )

    # So we don't actually try and clone anything
    mock_clone = mocker.patch("pytoil.cli.project.Repo.clone", autospec=True)

    # So we don't try and create a virtual environment
    # not what we're testing here
    mock_env_dispatcher = mocker.patch(
        "pytoil.cli.project.env_dispatcher", autospec=True, return_value=None
    )

    # So we don't actually open code
    mock_code_open = mocker.patch("pytoil.cli.project.VSCode.open", autospec=True)

    result = runner.invoke(app, ["project", "checkout", "remote1"])
    assert result.exit_code == 0

    assert "Project: 'remote1' found on your GitHub. Cloning..." in result.stdout
    mock_clone.assert_called_once()
    mock_env_dispatcher.assert_called_once()

    assert "Unable to auto-detect virtual environment. Skipping." in result.stdout
    assert "Opening 'remote1' in VSCode..." in result.stdout
    mock_code_open.assert_called_once()


def test_checkout_remote_correctly_sets_up_virtual_environment(
    mocker: MockerFixture, fake_projects_dir
):

    fake_config = Config(
        username="test",
        token="testtoken",
        projects_dir=fake_projects_dir,
        vscode=False,
    )

    mocker.patch(
        "pytoil.cli.project.Config.get",
        autospec=True,
        return_value=fake_config,
    )

    mocker.patch(
        "pytoil.cli.project.Repo.exists_local", autospec=True, return_value=False
    )

    mocker.patch(
        "pytoil.cli.project.Repo.exists_remote", autospec=True, return_value=True
    )

    # So we don't actually try and clone anything
    mock_clone = mocker.patch("pytoil.cli.project.Repo.clone", autospec=True)

    fake_project = fake_projects_dir.joinpath("virtualenv_project")

    fake_venv = VirtualEnv(project_path=fake_project)

    # Force a VirtualEnv
    mock_env_dispatcher = mocker.patch(
        "pytoil.cli.project.env_dispatcher", autospec=True, return_value=fake_venv
    )

    mock_venv_create = mocker.patch(
        "pytoil.cli.project.VirtualEnv.create", autospec=True
    )

    mock_code_open = mocker.patch("pytoil.cli.project.VSCode.open", autospec=True)
    mock_code_ppath = mocker.patch(
        "pytoil.cli.project.VSCode.set_python_path", autospec=True
    )

    result = runner.invoke(app, ["project", "checkout", "virtualenv_project"])
    assert result.exit_code == 0

    assert (
        "Project: 'virtualenv_project' found on your GitHub. Cloning..."
        in result.stdout
    )
    mock_clone.assert_called_once()
    mock_env_dispatcher.assert_called_once()
    assert "Auto-creating correct virtual environment..." in result.stdout
    mock_venv_create.assert_called_once()
    mock_code_ppath.assert_not_called()
    mock_code_open.assert_not_called()


def test_checkout_remote_correctly_sets_up_conda_environment(
    mocker: MockerFixture, fake_projects_dir
):

    fake_config = Config(
        username="test",
        token="testtoken",
        projects_dir=fake_projects_dir,
        vscode=False,
    )

    mocker.patch(
        "pytoil.cli.project.Config.get",
        autospec=True,
        return_value=fake_config,
    )

    mocker.patch(
        "pytoil.cli.project.Repo.exists_local", autospec=True, return_value=False
    )

    mocker.patch(
        "pytoil.cli.project.Repo.exists_remote", autospec=True, return_value=True
    )

    # So we don't actually try and clone anything
    mock_clone = mocker.patch("pytoil.cli.project.Repo.clone", autospec=True)

    fake_project = fake_projects_dir.joinpath("conda_project")

    fake_venv = CondaEnv(name="conda_project", project_path=fake_project)

    # Force a VirtualEnv
    mock_env_dispatcher = mocker.patch(
        "pytoil.cli.project.env_dispatcher", autospec=True, return_value=fake_venv
    )

    mock_conda_create = mocker.patch(
        "pytoil.cli.project.CondaEnv.create", autospec=True
    )

    mock_code_open = mocker.patch("pytoil.cli.project.VSCode.open", autospec=True)

    result = runner.invoke(app, ["project", "checkout", "conda_project"])
    assert result.exit_code == 0

    assert "Project: 'conda_project' found on your GitHub. Cloning..." in result.stdout
    mock_clone.assert_called_once()
    mock_env_dispatcher.assert_called_once()
    assert "Auto-creating correct virtual environment..." in result.stdout
    mock_conda_create.assert_called_once()
    mock_code_open.assert_not_called()


def test_checkout_remote_correctly_sets_up_virtual_environment_with_code(
    mocker: MockerFixture, fake_projects_dir
):

    fake_config = Config(
        username="test",
        token="testtoken",
        projects_dir=fake_projects_dir,
        vscode=True,
    )

    mocker.patch(
        "pytoil.cli.project.Config.get",
        autospec=True,
        return_value=fake_config,
    )

    mocker.patch(
        "pytoil.cli.project.Repo.exists_local", autospec=True, return_value=False
    )

    mocker.patch(
        "pytoil.cli.project.Repo.exists_remote", autospec=True, return_value=True
    )

    # So we don't actually try and clone anything
    mock_clone = mocker.patch("pytoil.cli.project.Repo.clone", autospec=True)

    fake_project = fake_projects_dir.joinpath("virtualenv_project")

    fake_venv = VirtualEnv(project_path=fake_project)

    # Force a VirtualEnv
    mock_env_dispatcher = mocker.patch(
        "pytoil.cli.project.env_dispatcher", autospec=True, return_value=fake_venv
    )

    mock_venv_create = mocker.patch(
        "pytoil.cli.project.VirtualEnv.create", autospec=True
    )

    mock_code_open = mocker.patch("pytoil.cli.project.VSCode.open", autospec=True)
    mock_code_ppath = mocker.patch(
        "pytoil.cli.project.VSCode.set_python_path", autospec=True
    )

    result = runner.invoke(app, ["project", "checkout", "virtualenv_project"])
    assert result.exit_code == 0

    assert (
        "Project: 'virtualenv_project' found on your GitHub. Cloning..."
        in result.stdout
    )
    mock_clone.assert_called_once()
    mock_env_dispatcher.assert_called_once()
    assert "Auto-creating correct virtual environment..." in result.stdout
    mock_venv_create.assert_called_once()
    assert "Setting 'python.pythonPath' in VSCode workspace..." in result.stdout
    mock_code_ppath.assert_called_once()
    assert "Opening 'virtualenv_project' in VSCode..." in result.stdout
    mock_code_open.assert_called_once()


def test_checkout_remote_correctly_sets_up_conda_environment_with_code(
    mocker: MockerFixture, fake_projects_dir
):

    fake_config = Config(
        username="test",
        token="testtoken",
        projects_dir=fake_projects_dir,
        vscode=True,
    )

    mocker.patch(
        "pytoil.cli.project.Config.get",
        autospec=True,
        return_value=fake_config,
    )

    mocker.patch(
        "pytoil.cli.project.Repo.exists_local", autospec=True, return_value=False
    )

    mocker.patch(
        "pytoil.cli.project.Repo.exists_remote", autospec=True, return_value=True
    )

    # So we don't actually try and clone anything
    mock_clone = mocker.patch("pytoil.cli.project.Repo.clone", autospec=True)

    fake_project = fake_projects_dir.joinpath("conda_project")

    fake_venv = CondaEnv(name="conda_project", project_path=fake_project)

    # Force a VirtualEnv
    mock_env_dispatcher = mocker.patch(
        "pytoil.cli.project.env_dispatcher", autospec=True, return_value=fake_venv
    )

    mock_venv_create = mocker.patch("pytoil.cli.project.CondaEnv.create", autospec=True)

    mock_code_open = mocker.patch("pytoil.cli.project.VSCode.open", autospec=True)
    mock_code_ppath = mocker.patch(
        "pytoil.cli.project.VSCode.set_python_path", autospec=True
    )

    result = runner.invoke(app, ["project", "checkout", "conda_project"])
    assert result.exit_code == 0

    assert "Project: 'conda_project' found on your GitHub. Cloning..." in result.stdout
    mock_clone.assert_called_once()
    mock_env_dispatcher.assert_called_once()
    assert "Auto-creating correct virtual environment..." in result.stdout
    mock_venv_create.assert_called_once()
    assert "Setting 'python.pythonPath' in VSCode workspace..." in result.stdout
    mock_code_ppath.assert_called_once()
    assert "Opening 'conda_project' in VSCode..." in result.stdout
    mock_code_open.assert_called_once()
