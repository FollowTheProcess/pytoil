"""
Tests for the config CLI command.

Author: Tom Fleet
Created: 09/03/2021
"""

import pytest
import yaml
from pytest_mock import MockerFixture
from typer.testing import CliRunner

import pytoil
from pytoil.cli.main import app

runner = CliRunner()


def test_config_show_displays_correctly(mocker: MockerFixture, temp_config_file):

    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

        result = runner.invoke(app, ["config", "show"])
        assert result.exit_code == 0

        assert "username: 'tempfileuser'" in result.stdout
        assert "token: 'tempfiletoken'" in result.stdout
        assert "projects_dir: '/Users/tempfileuser/projects'" in result.stdout
        assert "vscode: True" in result.stdout


@pytest.mark.parametrize(
    "key, value, option",
    [
        ("username", "usernamesetbytest", "--username"),
        ("username", "usernamesetbytest", "-u"),
        ("token", "tokensetbytest", "--token"),
        ("token", "tokensetbytest", "-t"),
        ("projects_dir", "/Users/test/projects", "--projects-dir"),
        ("projects_dir", "/Users/test/projects", "-p"),
        ("vscode", True, "--vscode"),
        ("vscode", True, "-v"),
        ("vscode", False, "--vscode"),
        ("vscode", False, "-v"),
    ],
)
def test_config_set_alters_correct_key_value_pair(
    mocker: MockerFixture, temp_config_file, key, value, option
):

    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

        # value must be a cast to a string here due to the use of
        # boolean in vscode option
        result = runner.invoke(app, ["config", "set", option, f"{value}"])
        assert result.exit_code == 0
        assert "Config updated successfully" in result.stdout

        # Load the written config
        with open(temp_config_file) as f:
            new_config_dict = yaml.full_load(f)

        assert new_config_dict.get(key) == value


@pytest.mark.parametrize(
    "bad_vscode_value", ["Yes", "No", "Notbool", "hello", "dingle", "15", "0", "1"]
)
def test_config_set_raises_bad_parameter_if_vscode_not_boolean(
    mocker: MockerFixture, temp_config_file, bad_vscode_value
):

    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

        result = runner.invoke(app, ["config", "set", "--vscode", bad_vscode_value])
        assert result.exit_code == 2
        assert "vscode must be a boolean value." in result.stdout

        # Make sure it works the same with both options
        result = runner.invoke(app, ["config", "set", "-v", bad_vscode_value])
        assert result.exit_code == 2
        assert "vscode must be a boolean value." in result.stdout


@pytest.mark.parametrize(
    "string, boolean",
    [
        ("True", True),
        ("TRUE", True),
        ("TrUe", True),
        ("true", True),
        ("False", False),
        ("FALSE", False),
        ("FaLsE", False),
        ("false", False),
    ],
)
def test_config_set_vscode_correctly_converts_str_to_bool(
    mocker: MockerFixture, temp_config_file, string, boolean
):

    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

        result = runner.invoke(app, ["config", "set", "--vscode", string])
        assert result.exit_code == 0

        assert "Config updated successfully" in result.stdout

        # Load the written config
        with open(temp_config_file) as f:
            new_config_dict = yaml.full_load(f)

        assert new_config_dict.get("vscode") == boolean
