"""
Tests for the primary pytoil command.

Author: Tom Fleet
Created: 08/03/2021
"""

from typing import Dict, List, Union

import pytest
import yaml
from pytest_mock import MockerFixture
from typer.testing import CliRunner

import pytoil
from pytoil import __version__
from pytoil.cli.main import app

runner = CliRunner()

# List of currently implemented commands
CMDS: List[str] = ["config", "init", "project", "show", "sync"]


@pytest.mark.parametrize("option", ["--version", "-V"])
def test_version_option(option):

    result = runner.invoke(app, [option])
    assert result.exit_code == 0
    assert result.stdout == f"pytoil version: {__version__}\n"


def test_help_option():

    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0

    # Assert each command shows up
    for cmd in CMDS:
        assert cmd in result.stdout


@pytest.mark.parametrize(
    "username, token, projects_dir, vscode",
    [
        ("me", "sometoken", "/Users/me/projects", True),
        ("someone", "difftoken", "/Users/someone/projects", False),
        ("whoknows", "whattoken", "/Users/whoknows/Development", True),
    ],
)
def test_init_writes_correct_config_with_input(
    mocker: MockerFixture, temp_config_file, username, token, projects_dir, vscode
):

    # Mock the config file
    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

        # Trick it into thinking it doesnt exist so it will write a new one
        mocker.patch(
            "pytoil.cli.main.pathlib.Path.exists", autospec=True, return_value=False
        )

        result = runner.invoke(
            app,
            ["init"],
            input=f"{username}\n{token}\n{projects_dir}\n{vscode}",
        )
        assert result.exit_code == 0

        with open(temp_config_file) as f:
            actual_new_config: Dict[str, Union[str, bool]] = yaml.full_load(f)

        expected_new_config: Dict[str, Union[str, bool]] = {
            "username": f"{username}",
            "token": f"{token}",
            "projects_dir": f"{projects_dir}",
            "vscode": vscode,
        }

        assert actual_new_config == expected_new_config

        assert "Config written" in result.stdout


def test_init_raises_if_vscode_is_not_boolean_string(
    mocker: MockerFixture, temp_config_file
):

    # Mock the config file
    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

        # Trick it into thinking it doesnt exist so it will write a new one
        mocker.patch(
            "pytoil.cli.main.pathlib.Path.exists", autospec=True, return_value=False
        )

        result = runner.invoke(
            app,
            ["init"],
            input="GitHub Username\nGitHub Token\n/Users/me/projects\nNotBool",
        )
        assert result.exit_code == 2
        assert "VSCode must be a boolean value" in result.stdout


def test_init_does_nothing_if_config_file_already_exists(
    mocker: MockerFixture, temp_config_file
):

    # Mock the config file
    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

        result = runner.invoke(
            app,
            ["init"],
        )
        assert result.exit_code == 0

        assert "You're all set!" in result.stdout
