"""
Tests for the VSCode opening and settings
logic.

Author: Tom Fleet
Created: 06/03/2021
"""

import json
import pathlib
import subprocess

import pytest
from pytest_mock import MockerFixture

from pytoil.exceptions import CodeNotInstalledError
from pytoil.vscode import VSCode


def test_vscode_init():

    fake_project = pathlib.Path("fakeproject")

    code = VSCode(root=fake_project)

    assert code.root == fake_project.resolve()


def test_vscode_repr():

    fake_project = pathlib.Path("fakeproject")

    code = VSCode(root=fake_project)

    assert code.__repr__() == f"VSCode(root={fake_project.resolve()!r})"


def test_vscode_raise_if_not_installed_works_on_missing_code(mocker: MockerFixture):

    # Mock out the return from shutil.which to be False
    mocker.patch("pytoil.vscode.shutil.which", autospec=True, return_value=False)

    fake_project = pathlib.Path("/Users/me/project1")

    with pytest.raises(CodeNotInstalledError):
        code = VSCode(root=fake_project)
        code.raise_if_not_installed()


def test_vscode_raise_if_not_installed_does_nothing_when_code_installed(
    mocker: MockerFixture,
):

    # Mock out the return from shutil.which to be True
    mocker.patch("pytoil.vscode.shutil.which", autospec=True, return_value=True)

    fake_project = pathlib.Path("/Users/me/project1")

    # If this raises, the test fails
    code = VSCode(root=fake_project)
    code.raise_if_not_installed()


def test_vscode_open_passes_correct_command_to_subprocess(mocker: MockerFixture):

    # Mock out the raise_if_not_installed call
    mocker.patch(
        "pytoil.vscode.VSCode.raise_if_not_installed", autospec=True, return_value=None
    )

    mock_subprocess = mocker.patch("pytoil.vscode.subprocess.run", autospec=True)

    fake_project = pathlib.Path("/Users/me/project1")

    code = VSCode(root=fake_project)

    code.open()

    mock_subprocess.assert_called_once_with(
        ["code", f"{fake_project.resolve()}"], check=True
    )


def test_vscode_open_raises_on_subprocess_error(mocker: MockerFixture):

    # Mock out the raise_if_not_installed call
    mocker.patch(
        "pytoil.vscode.VSCode.raise_if_not_installed", autospec=True, return_value=None
    )

    mocker.patch(
        "pytoil.vscode.subprocess.run",
        autospec=True,
        side_effect=[subprocess.CalledProcessError(-1, "cmd")],
    )

    fake_project = pathlib.Path("/Users/me/project1")

    code = VSCode(root=fake_project)

    with pytest.raises(subprocess.CalledProcessError):
        code.open()


def test_vscode_set_python_path(fake_vscode_workspace_settings):

    with open(fake_vscode_workspace_settings, "r+") as f:
        settings_dict_before = json.load(f)
        python_path_before = settings_dict_before.get("python.pythonPath")

        code = VSCode(root=fake_vscode_workspace_settings.parents[1])

        new_python_path = pathlib.Path(
            "/Users/me/projects/fakeproject/.venv/bin/python"
        )

        code.set_python_path(python_path=new_python_path)

        assert python_path_before == "/usr/bin/python"

        settings_dict_after = json.load(f)
        python_path_after = settings_dict_after.get("python.pythonPath")

        assert python_path_after == "/Users/me/projects/fakeproject/.venv/bin/python"
