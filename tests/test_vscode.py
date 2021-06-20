"""
Tests for the vscode module.

Author: Tom Fleet
Created: 19/06/2021
"""

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict

import pytest
from pytest_mock import MockerFixture

from pytoil.exceptions import CodeNotInstalledError
from pytoil.vscode import VSCode


def test_vscode_init():

    code = VSCode(root=Path("somewhere"))

    assert code.root == Path("somewhere")
    assert code.code == shutil.which("code")


def test_vscode_init_passed():

    code = VSCode(root=Path("somewhere"), code="somecodebinary")

    assert code.root == Path("somewhere")
    assert code.code == "somecodebinary"


def test_vscode_repr():

    code = VSCode(root=Path("somewhere"), code="somecodebinary")

    assert repr(code) == f"VSCode(root={code.root!r}, code='somecodebinary')"


def test_raise_for_code_raises_if_code_is_none():

    code = VSCode(root=Path("somewhere"), code=None)

    with pytest.raises(CodeNotInstalledError):
        code.raise_for_code()


def test_open_raises_on_subprocess_error(mocker: MockerFixture):

    mocker.patch(
        "pytoil.vscode.vscode.subprocess.run",
        autospec=True,
        side_effect=[subprocess.CalledProcessError(-1, "cmd")],
    )

    code = VSCode(root=Path("somewhere"), code="code")

    with pytest.raises(subprocess.CalledProcessError):
        code.open()


def test_open_correctly_calls_code_executable(mocker: MockerFixture):

    mock_subprocess = mocker.patch("pytoil.vscode.vscode.subprocess.run", autospec=True)

    code = VSCode(root=Path("somewhere"), code="/path/to/code")

    code.open()

    mock_subprocess.assert_called_once_with(["/path/to/code", "somewhere"], check=True)


def test_vscode_set_python_path_works_on_non_existent_settings(fake_projects_dir):

    fake_project: Path = fake_projects_dir.joinpath("myproject")
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


def test_vscode_set_python_path_works_on_empty_file(fake_projects_dir):

    fake_project: Path = fake_projects_dir.joinpath("myproject")
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


def test_vscode_set_python_path_works_on_existing_settings(fake_projects_dir):

    fake_project: Path = fake_projects_dir.joinpath("myproject")
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
