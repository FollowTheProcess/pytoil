"""
Tests for the CLI sync command.

Author: Tom Fleet
Created: 11/04/2021
"""

from typing import List

import pytest
from pytest_mock import MockerFixture
from typer.testing import CliRunner

from pytoil.cli.main import app
from pytoil.config import Config

runner = CliRunner()


def test_sync_all_does_nothing_if_local_and_remote_are_synced(
    mocker: MockerFixture, fake_projects_dir
):

    fake_config = Config(
        username="test",
        token="testtoken",
        projects_dir=fake_projects_dir,
        vscode=True,
    )

    mocker.patch(
        "pytoil.cli.sync.Config.get",
        autospec=True,
        return_value=fake_config,
    )

    # We use the local project names as repos so everything is in sync
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

    # Make sure it doesn't actually clone anything
    mocker.patch("pytoil.repo.repo.Repo.clone", autospec=True, return_value=None)

    result = runner.invoke(app, ["sync", "all"])
    assert result.exit_code == 0

    assert (
        "All your remote repos already exist locally. Nothing to do!" in result.stdout
    )


def test_sync_all_respects_user_input_no(mocker: MockerFixture, fake_projects_dir):

    fake_config = Config(
        username="test",
        token="testtoken",
        projects_dir=fake_projects_dir,
        vscode=True,
    )

    mocker.patch(
        "pytoil.cli.sync.Config.get",
        autospec=True,
        return_value=fake_config,
    )

    # Now local and remotes are out of sync
    fake_repo_names: List[str] = [
        "repo1",
        "anotherrepo",
        "remote1",
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

    # Make sure it doesn't actually clone anything
    mocker.patch("pytoil.repo.repo.Repo.clone", autospec=True, return_value=None)

    # No force, will prompt user. Here we input n
    # should abort and not do anything
    result = runner.invoke(app, ["sync", "all"], input="n")
    assert result.exit_code == 1

    assert "Aborted" in result.stdout


def test_sync_all_respects_user_input_yes(mocker: MockerFixture, fake_projects_dir):

    fake_config = Config(
        username="test",
        token="testtoken",
        projects_dir=fake_projects_dir,
        vscode=True,
    )

    mocker.patch(
        "pytoil.cli.sync.Config.get",
        autospec=True,
        return_value=fake_config,
    )

    # Now local and remotes are out of sync
    fake_repo_names: List[str] = [
        "repo1",
        "anotherrepo",
        "remote1",
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

    # Make sure it doesn't actually clone anything
    mocker.patch("pytoil.repo.repo.Repo.clone", autospec=True, return_value=None)

    # No force, will prompt user. Here we input y
    # should now clone stuff
    result = runner.invoke(app, ["sync", "all"], input="y")
    assert result.exit_code == 0

    # Only first 3 are remote but not local
    assert "This will clone 3 repos" in result.stdout
    assert "Are you sure you want to proceed?" in result.stdout

    # Only first 3 are remote but not local
    for repo in fake_repo_names[:3]:
        assert f"Cloning: {repo!r}" in result.stdout


@pytest.mark.parametrize("force_flag", ["--force", "-f"])
def test_sync_all_respects_force_flag(
    mocker: MockerFixture, fake_projects_dir, force_flag
):

    fake_config = Config(
        username="test",
        token="testtoken",
        projects_dir=fake_projects_dir,
        vscode=True,
    )

    mocker.patch(
        "pytoil.cli.sync.Config.get",
        autospec=True,
        return_value=fake_config,
    )

    # Now local and remotes are out of sync
    fake_repo_names: List[str] = [
        "repo1",
        "anotherrepo",
        "remote1",
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

    # Make sure it doesn't actually clone anything
    mocker.patch("pytoil.repo.repo.Repo.clone", autospec=True, return_value=None)

    # Now we force, checking both flags work the same
    result = runner.invoke(app, ["sync", "all", force_flag])
    assert result.exit_code == 0

    # Only first 3 are remote but not local
    for repo in fake_repo_names[:3]:
        assert f"Cloning: {repo!r}" in result.stdout


def test_sync_these_does_nothing_if_local_and_remote_are_synced(
    mocker: MockerFixture, fake_projects_dir
):

    fake_config = Config(
        username="test",
        token="testtoken",
        projects_dir=fake_projects_dir,
        vscode=True,
    )

    mocker.patch(
        "pytoil.cli.sync.Config.get",
        autospec=True,
        return_value=fake_config,
    )

    # We use the local project names as repos so everything is in sync
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

    # Make sure it doesn't actually clone anything
    mocker.patch("pytoil.repo.repo.Repo.clone", autospec=True, return_value=None)

    # We use a subset of the already synced projects as arguments
    # to these
    # Shouldnt do anything
    result = runner.invoke(
        app, ["sync", "these", "project1", "dingleproject", "anotherone"]
    )
    assert result.exit_code == 0

    assert (
        "All your remote repos already exist locally. Nothing to do." in result.stdout
    )


def test_sync_these_respects_user_input_no(mocker: MockerFixture, fake_projects_dir):

    fake_config = Config(
        username="test",
        token="testtoken",
        projects_dir=fake_projects_dir,
        vscode=True,
    )

    mocker.patch(
        "pytoil.cli.sync.Config.get",
        autospec=True,
        return_value=fake_config,
    )

    # Now local and remotes are out of sync
    fake_repo_names: List[str] = [
        "repo1",
        "anotherrepo",
        "remote1",
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

    # Make sure it doesn't actually clone anything
    mocker.patch("pytoil.repo.repo.Repo.clone", autospec=True, return_value=None)

    # No force, will prompt user. Here we input n
    # should abort and not do anything
    result = runner.invoke(
        app, ["sync", "these", "repo1", "project1", "remote1"], input="n"
    )
    assert result.exit_code == 1

    assert "Aborted" in result.stdout


def test_sync_these_respects_user_input_yes(mocker: MockerFixture, fake_projects_dir):

    fake_config = Config(
        username="test",
        token="testtoken",
        projects_dir=fake_projects_dir,
        vscode=True,
    )

    mocker.patch(
        "pytoil.cli.sync.Config.get",
        autospec=True,
        return_value=fake_config,
    )

    # Now local and remotes are out of sync
    fake_repo_names: List[str] = [
        "repo1",
        "anotherrepo",
        "remote1",
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

    # Make sure it doesn't actually clone anything
    mocker.patch("pytoil.repo.repo.Repo.clone", autospec=True, return_value=None)

    # No force, will prompt user. Here we input y
    # should only clone repo1, anotherrepo, and remote1, project1 is already local
    result = runner.invoke(
        app,
        ["sync", "these", "repo1", "project1", "anotherrepo", "remote1"],
        input="y",
    )
    assert result.exit_code == 0

    # Only first 3 are remote but not local
    assert "This will clone 3 repos" in result.stdout
    assert "Are you sure you want to proceed?" in result.stdout

    # Only first 3 are remote but not local
    for repo in fake_repo_names[:3]:
        assert f"Cloning: {repo!r}" in result.stdout


@pytest.mark.parametrize("force_flag", ["--force", "-f"])
def test_sync_these_respects_force_flag(
    mocker: MockerFixture, fake_projects_dir, force_flag
):

    fake_config = Config(
        username="test",
        token="testtoken",
        projects_dir=fake_projects_dir,
        vscode=True,
    )

    mocker.patch(
        "pytoil.cli.sync.Config.get",
        autospec=True,
        return_value=fake_config,
    )

    # Now local and remotes are out of sync
    fake_repo_names: List[str] = [
        "repo1",
        "anotherrepo",
        "remote1",
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

    # Make sure it doesn't actually clone anything
    mocker.patch("pytoil.repo.repo.Repo.clone", autospec=True, return_value=None)

    # Now we force, checking both flags work the same
    result = runner.invoke(
        app,
        [
            "sync",
            "these",
            "repo1",
            "project1",
            "anotherrepo",
            "remote1",
            force_flag,
        ],
    )
    assert result.exit_code == 0

    # Only first 3 are remote but not local
    for repo in fake_repo_names[:3]:
        assert f"Cloning: {repo!r}" in result.stdout
