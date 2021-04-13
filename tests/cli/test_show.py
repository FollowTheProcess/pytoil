"""
Tests for the show CLI command.

Author: Tom Fleet
Created: 11/04/2021
"""

from typing import List

from pytest_mock import MockerFixture
from typer.testing import CliRunner

import pytoil
from pytoil.cli.main import app
from pytoil.config import Config

runner = CliRunner()


def test_show_local_returns_correct_directory_names(
    mocker: MockerFixture, fake_projects_dir
):

    fake_config = Config(
        username="test",
        token="testtoken",
        projects_dir=fake_projects_dir,
        vscode=True,
    )

    mocker.patch(
        "pytoil.cli.show.Config.get",
        autospec=True,
        return_value=fake_config,
    )

    result = runner.invoke(app, ["show", "local"])
    assert result.exit_code == 0
    assert "Local projects" in result.stdout

    assert "project1" in result.stdout
    assert "myproject" in result.stdout
    assert "dingleproject" in result.stdout
    assert "anotherone" in result.stdout

    assert ".ishouldnt_show_up" not in result.stdout


def test_show_local_returns_special_message_if_no_local_projects(
    mocker: MockerFixture, empty_projects_dir
):

    fake_config = Config(
        username="test",
        token="testtoken",
        projects_dir=empty_projects_dir,
        vscode=True,
    )

    mocker.patch(
        "pytoil.cli.show.Config.get",
        autospec=True,
        return_value=fake_config,
    )

    result = runner.invoke(app, ["show", "local"])
    assert result.exit_code == 0

    assert "You don't have any local projects yet!" in result.stdout


def test_show_remote_returns_correct_project_names(
    mocker: MockerFixture, temp_config_file
):

    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

        fake_repo_names: List[str] = ["repo1", "hellorepo", "myrepo", "anotherrepo"]

        mocker.patch(
            "pytoil.api.api.API.get_repo_names",
            autospec=True,
            return_value=fake_repo_names,
        )

        result = runner.invoke(app, ["show", "remote"])
        assert result.exit_code == 0
        assert "Remote projects" in result.stdout

        for repo in fake_repo_names:
            assert repo in result.stdout


def test_show_remote_returns_special_message_if_no_remote_projects(
    mocker: MockerFixture, temp_config_file
):

    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

        fake_repo_names: List[str] = []

        mocker.patch(
            "pytoil.api.api.API.get_repo_names",
            autospec=True,
            return_value=fake_repo_names,
        )

        result = runner.invoke(app, ["show", "remote"])
        assert result.exit_code == 0
        assert "You don't have any remote projects yet!" in result.stdout


def test_show_all_returns_both_correctly(mocker: MockerFixture, fake_projects_dir):

    fake_config = Config(
        username="test",
        token="testtoken",
        projects_dir=fake_projects_dir,
        vscode=True,
    )

    mocker.patch(
        "pytoil.cli.show.Config.get",
        autospec=True,
        return_value=fake_config,
    )

    fake_repo_names: List[str] = ["repo1", "hellorepo", "myrepo", "anotherrepo"]

    mocker.patch(
        "pytoil.api.api.API.get_repo_names",
        autospec=True,
        return_value=fake_repo_names,
    )

    result = runner.invoke(app, ["show", "all"])
    assert result.exit_code == 0

    assert "Local projects" in result.stdout
    assert "Remote projects" in result.stdout

    assert "project1" in result.stdout
    assert "myproject" in result.stdout
    assert "dingleproject" in result.stdout
    assert "anotherone" in result.stdout

    assert ".ishouldnt_show_up" not in result.stdout

    for repo in fake_repo_names:
        assert repo in result.stdout


def test_show_all_returns_special_message_if_no_local_projects(
    mocker: MockerFixture, empty_projects_dir
):

    # Here we have remotes but no locals
    fake_repo_names: List[str] = ["repo1", "hellorepo", "myrepo", "anotherrepo"]

    mocker.patch(
        "pytoil.api.api.API.get_repo_names",
        autospec=True,
        return_value=fake_repo_names,
    )

    fake_config = Config(
        username="test",
        token="testtoken",
        projects_dir=empty_projects_dir,
        vscode=True,
    )

    mocker.patch(
        "pytoil.cli.show.Config.get",
        autospec=True,
        return_value=fake_config,
    )

    result = runner.invoke(app, ["show", "all"])
    assert result.exit_code == 0

    assert "You don't have any local projects yet!" in result.stdout

    # Should still show remotes
    assert "Remote projects" in result.stdout

    for repo in fake_repo_names:
        assert repo in result.stdout


def test_show_all_returns_special_message_if_no_remote_projects(
    mocker: MockerFixture, fake_projects_dir
):

    # Here we have locals but no remotes
    fake_repo_names: List[str] = []

    mocker.patch(
        "pytoil.api.api.API.get_repo_names",
        autospec=True,
        return_value=fake_repo_names,
    )

    fake_config = Config(
        username="test",
        token="testtoken",
        projects_dir=fake_projects_dir,
        vscode=True,
    )

    mocker.patch(
        "pytoil.cli.show.Config.get",
        autospec=True,
        return_value=fake_config,
    )

    result = runner.invoke(app, ["show", "all"])
    assert result.exit_code == 0

    assert "You don't have any remote projects yet!" in result.stdout

    # Should still show locals
    assert "Local projects" in result.stdout

    assert "project1" in result.stdout
    assert "myproject" in result.stdout
    assert "dingleproject" in result.stdout
    assert "anotherone" in result.stdout

    assert ".ishouldnt_show_up" not in result.stdout


def test_show_diff_shows_what_wed_expect(mocker: MockerFixture, fake_projects_dir):

    fake_config = Config(
        username="test",
        token="testtoken",
        projects_dir=fake_projects_dir,
        vscode=True,
    )

    mocker.patch(
        "pytoil.cli.show.Config.get",
        autospec=True,
        return_value=fake_config,
    )

    # This time add some locals in so we can work out the diff
    fake_repo_names: List[str] = [
        "repo1",
        "hellorepo",
        "myrepo",
        "anotherrepo",
        "project1",
        "myproject",
        "dingleproject",
        "anotherone",
    ]

    mocker.patch(
        "pytoil.api.api.API.get_repo_names",
        autospec=True,
        return_value=fake_repo_names,
    )

    # Now the diff is just the repos
    actual_diff: List[str] = [
        "repo1",
        "hellorepo",
        "myrepo",
        "anotherrepo",
    ]

    result = runner.invoke(app, ["show", "diff"])
    assert result.exit_code == 0
    assert "Remote projects that are not local" in result.stdout

    for project in actual_diff:
        assert project in result.stdout


def test_show_diff_shows_special_message_if_local_and_remote_are_synced(
    mocker: MockerFixture, fake_projects_dir
):

    fake_config = Config(
        username="test",
        token="testtoken",
        projects_dir=fake_projects_dir,
        vscode=True,
    )

    mocker.patch(
        "pytoil.cli.show.Config.get",
        autospec=True,
        return_value=fake_config,
    )

    # Now our fake repo names exactly match the set of local projects
    fake_repo_names: List[str] = [
        "project1",
        "myproject",
        "dingleproject",
        "anotherone",
    ]

    mocker.patch(
        "pytoil.api.api.API.get_repo_names",
        autospec=True,
        return_value=fake_repo_names,
    )

    result = runner.invoke(app, ["show", "diff"])
    assert result.exit_code == 0
    assert (
        "Your local and remote projects are all synced up. Nothing to show!"
        in result.stdout
    )
