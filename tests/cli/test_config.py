"""
Tests for the config CLI command.

Author: Tom Fleet
Created: 11/04/2021
"""

from pytest_mock import MockerFixture
from typer.testing import CliRunner

import pytoil
from pytoil.cli.main import app

runner = CliRunner()


def test_config_show_displays_correctly(mocker: MockerFixture, temp_config_file):

    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

        result = runner.invoke(app, ["config"])
        assert result.exit_code == 0

        assert "username: 'tempfileuser'" in result.stdout
        assert "token: 'tempfiletoken'" in result.stdout
        assert "projects_dir: '/Users/tempfileuser/projects'" in result.stdout
        assert "vscode: True" in result.stdout


def test_config_show_correctly_handles_file_not_found_error(
    mocker: MockerFixture, temp_config_file
):

    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

        mocker.patch(
            "pytoil.config.config.Config.get",
            autospec=True,
            side_effect=[FileNotFoundError()],
        )

        result = runner.invoke(app, ["config"])
        assert result.exit_code == 0
        assert "No config file yet!" in result.stdout
