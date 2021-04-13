"""
Test for version callback.

Author: Tom Fleet
Created: 13/04/2021
"""

import pytest
from typer.testing import CliRunner

from pytoil import __version__
from pytoil.cli.main import app

runner = CliRunner()


@pytest.mark.parametrize("version_flag", ["--version", "-V"])
def test_version_flag_correctly_displays_actual_version(version_flag):

    result = runner.invoke(app, [version_flag])
    assert result.exit_code == 0
    assert f"pytoil version: {__version__}" in result.stdout
