"""
Tests for the project remove CLI command.

Author: Tom Fleet
Created: 11/03/2021
"""

import pytest
from pytest_mock import MockerFixture
from typer.testing import CliRunner

from pytoil.cli.main import app
from pytoil.config import Config

runner = CliRunner()


def test_remove_aborts_if_project_doesnt_exist(
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

    # Try to remove a project thats not in our fake directory
    result = runner.invoke(app, ["project", "remove", "i_was_never_here"])
    assert result.exit_code == 1
    assert "Project: 'i_was_never_here' not found in local filesystem" in result.stdout
    assert "Aborted!" in result.stdout


def test_remove_respects_no_input_on_confirmation(
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

    # Make sure the path exists before
    assert fake_projects_dir.joinpath("myproject").exists()

    # Now we try and remove one that does exist, but without --force
    # simulate user input 'n'
    result = runner.invoke(app, ["project", "remove", "myproject"], input="n\n")
    assert "This will remove 'myproject' from your local filesystem" in result.stdout
    assert "Are you sure?" in result.stdout
    assert result.exit_code == 1
    assert "Aborted!" in result.stdout

    # Make sure it didn't actually delete it despite aborting
    assert fake_projects_dir.joinpath("myproject").exists()


def test_remove_respects_yes_input_on_confirmation(
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

    # Make sure the path exists before
    assert fake_projects_dir.joinpath("myproject").exists()

    # Now we try and remove one that does exist, but without --force
    # simulate user input 'y'
    result = runner.invoke(app, ["project", "remove", "myproject"], input="y\n")
    assert "This will remove 'myproject' from your local filesystem" in result.stdout
    assert "Are you sure?" in result.stdout
    assert "Removing project: 'myproject'." in result.stdout
    assert "Done!" in result.stdout
    assert result.exit_code == 0

    # Make sure it performed the deletion
    assert not fake_projects_dir.joinpath("myproject").exists()


@pytest.mark.parametrize("force_flag", ["--force", "-f"])
def test_remove_respects_force_flag(
    mocker: MockerFixture, fake_projects_dir, force_flag
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

    # Make sure the path exists before
    assert fake_projects_dir.joinpath("myproject").exists()

    # Here we remove it but force deletion, shouldn't prompt to confirm
    result = runner.invoke(app, ["project", "remove", "myproject", force_flag])
    assert (
        "This will remove 'myproject' from your local filesystem" not in result.stdout
    )
    assert "Are you sure?" not in result.stdout

    assert "Removing project: 'myproject'." in result.stdout
    assert "Done!" in result.stdout
    assert result.exit_code == 0

    # Make sure it performed the deletion
    assert not fake_projects_dir.joinpath("myproject").exists()
