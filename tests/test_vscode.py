import json
import sys
from pathlib import Path
from typing import Any, Dict

import pytest
from pytest_mock import MockerFixture

from pytoil.exceptions import CodeNotInstalledError
from pytoil.vscode import VSCode
from pytoil.vscode.vscode import WORKSPACE_PYTHON_SETTING


@pytest.mark.asyncio
async def test_open_raises_if_code_is_not_installed():
    code = VSCode(root=Path("somewhere"), code=None)

    with pytest.raises(CodeNotInstalledError):
        await code.open()


@pytest.mark.asyncio
async def test_open_passes_correct_args_to_subprocess(mocker: MockerFixture):
    mock = mocker.patch(
        "pytoil.vscode.vscode.asyncio.create_subprocess_exec", autospec=True
    )

    code = VSCode(Path("somewhere"), "notcode")

    await code.open()

    mock.assert_called_once_with(
        "notcode", ".", cwd=Path("somewhere"), stdout=sys.stdout, stderr=sys.stderr
    )


@pytest.mark.asyncio
async def test_vscode_set_workspace_python_works_on_non_existent_settings(
    fake_projects_dir,
):

    fake_project: Path = fake_projects_dir.joinpath("myproject")
    settings = fake_project.joinpath(".vscode/settings.json")

    code = VSCode(root=fake_project)

    ppath = fake_project.joinpath("/usr/bin/sillypython")

    # Assert no settings before
    assert not settings.exists()

    # Set the python path
    await code.set_workspace_python(ppath)

    # Now it should exist
    assert settings.exists()

    # Get contents
    with open(settings, encoding="utf-8") as f:
        written_settings_dict: Dict[str, Any] = json.load(f)

    expected: Dict[str, Any] = {WORKSPACE_PYTHON_SETTING: f"{ppath.resolve()}"}

    assert written_settings_dict == expected


@pytest.mark.asyncio
async def test_vscode_set_workspace_python_works_on_existing_settings(
    fake_projects_dir,
):

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
        WORKSPACE_PYTHON_SETTING: "/usr/bin/python",
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
        WORKSPACE_PYTHON_SETTING: "/usr/bin/sillypython",
        "python.testing.pytestEnabled": False,
    }

    await code.set_workspace_python(python_path=ppath)

    # Get new contents
    with open(settings, encoding="utf-8") as f:
        written_settings_dict: Dict[str, Any] = json.load(f)

    assert written_settings_dict == expected
