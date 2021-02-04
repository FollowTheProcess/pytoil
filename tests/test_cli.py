"""
Tests for the main CLI.

Currently it just echos whilst I decide the structure.
Similarly, these tests are just placeholders.

Author: Tom Fleet
Created: 04/02/2021
"""

import pytest
from typer.testing import CliRunner

from pytoil import __version__
from pytoil.cli import app

runner = CliRunner()


def test_no_args_is_help():
    result = runner.invoke(app)
    assert result.exit_code == 0
    assert "Helpful CLI to automate the development workflow!" in result.stdout


@pytest.mark.parametrize("option", ["--version", "-V"])
def test_version(option):
    result = runner.invoke(app, [option])
    assert result.exit_code == 0
    assert f"pytoil version: {__version__}" in result.stdout


def test_new():
    result = runner.invoke(app, ["new", "dingle"])
    assert result.exit_code == 0
    assert "Creating project: dingle" in result.stdout


@pytest.mark.parametrize("option", ["--cookiecutter", "-c"])
def test_new_with_cookiecutter(option):
    result = runner.invoke(app, ["new", option, "dingle"])
    assert result.exit_code == 0
    assert "Creating project: dingle with cookiecutter." in result.stdout


def test_resume():
    result = runner.invoke(app, ["resume", "dingle"])
    assert result.exit_code == 0
    assert "Resuming project: dingle" in result.stdout
