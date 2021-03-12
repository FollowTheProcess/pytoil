"""
Tests for the VSCode opening and settings
logic.

Author: Tom Fleet
Created: 06/03/2021
"""

import json
import pathlib
import subprocess
from typing import Any, Dict

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
    mocker.patch("pytoil.vscode.vscode.shutil.which", autospec=True, return_value=False)

    fake_project = pathlib.Path("/Users/me/project1")

    with pytest.raises(CodeNotInstalledError):
        code = VSCode(root=fake_project)
        code.raise_if_not_installed()


def test_vscode_raise_if_not_installed_does_nothing_when_code_installed(
    mocker: MockerFixture,
):

    # Mock out the return from shutil.which to be True
    mocker.patch("pytoil.vscode.vscode.shutil.which", autospec=True, return_value=True)

    fake_project = pathlib.Path("/Users/me/project1")

    # If this raises, the test fails
    code = VSCode(root=fake_project)
    code.raise_if_not_installed()


def test_vscode_open_passes_correct_command_to_subprocess(mocker: MockerFixture):

    # Mock out the raise_if_not_installed call
    mocker.patch(
        "pytoil.vscode.VSCode.raise_if_not_installed", autospec=True, return_value=None
    )

    mock_subprocess = mocker.patch("pytoil.vscode.vscode.subprocess.run", autospec=True)

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
        "pytoil.vscode.vscode.subprocess.run",
        autospec=True,
        side_effect=[subprocess.CalledProcessError(-1, "cmd")],
    )

    fake_project = pathlib.Path("/Users/me/project1")

    code = VSCode(root=fake_project)

    with pytest.raises(subprocess.CalledProcessError):
        code.open()


def test_vscode_set_python_path_works_on_non_existent_settings(
    mocker: MockerFixture, fake_projects_dir
):

    fake_project: pathlib.Path = fake_projects_dir.joinpath("myproject")
    settings = fake_project.joinpath(".vscode/settings.json")

    code = VSCode(root=fake_project)

    ppath = fake_project.joinpath("/usr/bin/sillypython")

    # Assert no settings before
    assert not settings.exists()

    # Set the python path
    code.set_python_path(ppath)

    # Now it should exist
    assert settings.exists()

    # Get contents
    with open(settings, mode="r", encoding="utf-8") as f:
        written_settings_dict: Dict[str, Any] = json.load(f)

    expected: Dict[str, Any] = {"python.pythonPath": f"{ppath.resolve()}"}

    assert written_settings_dict == expected


def test_vscode_set_python_path_works_on_existing_settings(
    mocker: MockerFixture, fake_projects_dir
):

    fake_project: pathlib.Path = fake_projects_dir.joinpath("myproject")
    settings = fake_project.joinpath(".vscode/settings.json")
    settings.parent.mkdir()
    settings.touch()

    code = VSCode(root=fake_project)

    ppath = fake_project.joinpath("/usr/bin/sillypython")

    settings_dict: Dict[str, Any] = {
        "editor.suggestSelection": True,
        "code-runner.runInTerminal": False,
        "python.linting.mypyEnabled": True,
        "python.linting.blackPath": "usr/bin/black",
        "randomSetting": "yes",
        "HowHardThisIsToComeUpWith": 10,
        "python.pythonPath": "/usr/bin/python",
        "python.testing.pytestEnabled": False,
    }

    # Write our fake settings to the right place
    with open(settings, mode="w", encoding="utf-8") as f:
        json.dump(settings_dict, f, sort_keys=True, indent=4)

    assert settings.exists()

    expected: Dict[str, Any] = {
        "editor.suggestSelection": True,
        "code-runner.runInTerminal": False,
        "python.linting.mypyEnabled": True,
        "python.linting.blackPath": "usr/bin/black",
        "randomSetting": "yes",
        "HowHardThisIsToComeUpWith": 10,
        "python.pythonPath": "/usr/bin/sillypython",
        "python.testing.pytestEnabled": False,
    }

    code.set_python_path(python_path=ppath)

    # Get new contents
    with open(settings, mode="r", encoding="utf-8") as f:
        written_settings_dict: Dict[str, Any] = json.load(f)

    assert written_settings_dict == expected


def test_vscode_set_python_path_works_on_empty_file(
    mocker: MockerFixture, fake_projects_dir
):

    fake_project: pathlib.Path = fake_projects_dir.joinpath("myproject")
    settings = fake_project.joinpath(".vscode/settings.json")
    settings.parent.mkdir()
    settings.touch()

    code = VSCode(root=fake_project)

    ppath = fake_project.joinpath("/usr/bin/sillypython")

    assert settings.exists()

    # Assert it's empty
    assert len(settings.read_text()) == 0

    code.set_python_path(python_path=ppath)

    assert len(settings.read_text()) != 0

    # Get new contents
    with open(settings, mode="r", encoding="utf-8") as f:
        written_settings_dict: Dict[str, Any] = json.load(f)

    expected: Dict[str, Any] = {"python.pythonPath": f"{ppath.resolve()}"}

    assert written_settings_dict == expected
