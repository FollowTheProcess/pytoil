"""
Tests for the primary pytoil command.

Author: Tom Fleet
Created: 08/03/2021
"""

from typing import List

import pytest
from typer.testing import CliRunner

from pytoil import __version__
from pytoil.cli.main import app

runner = CliRunner()

# List of currently implemented commands
CMDS: List[str] = ["config", "project", "show", "sync"]


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
