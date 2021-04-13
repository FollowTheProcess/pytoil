"""
Tests for the project info CLI command.


Author: Tom Fleet
Created: 11/04/2021
"""

from typing import Dict, Union

from pytest_mock import MockerFixture
from typer.testing import CliRunner

from pytoil.cli.main import app
from pytoil.config import Config
from pytoil.exceptions import RepoNotFoundError

runner = CliRunner()


def test_info_displays_properly(mocker: MockerFixture, fake_projects_dir):

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

    return_dict: Dict[str, Union[str, int, bool]] = {
        "name": "dingle",
        "size": 2048,
        "remote": True,
        "local": True,
        "created_at": "12/02/20",
        "updated_at": "18/02/20",
    }

    # Patch out repo.info to return whatever dict we want
    mocker.patch("pytoil.cli.main.Repo.info", autospec=True, return_value=return_dict)

    result = runner.invoke(app, ["info", "myproject"])
    assert result.exit_code == 0
    assert "Info for: 'myproject'" in result.stdout

    for key, val in return_dict.items():
        assert f"{key}: {val}" in result.stdout


def test_info_handles_repo_not_found(mocker: MockerFixture, fake_projects_dir):

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

    # Make repo.info raise a RepoNotFoundError
    mocker.patch(
        "pytoil.cli.main.Repo.info",
        autospec=True,
        side_effect=[RepoNotFoundError("IT DOESNT EXIST YOU FOOL")],
    )

    # Now CLI should give nice message and abort
    result = runner.invoke(app, ["info", "someproject"])
    assert result.exit_code == 1
    assert "Project: 'someproject' not found locally or on GitHub." in result.stdout
    assert "Aborted!" in result.stdout
