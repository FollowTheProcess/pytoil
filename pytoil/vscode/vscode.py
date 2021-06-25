"""
Module implementing pytoils interface with VSCode.

Author: Tom Fleet
Created: 19/06/2021
"""

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

from pytoil.exceptions import CodeNotInstalledError

# From VSCode 1.57.1 the 'python.pythonPath' setting is being
# deprecated in favour of 'python.defaultInterpreterPath'
# it works in a slightly different way but for us it's effectively
# a straight swap
WORKSPACE_PYTHON_SETTING: str = "python.defaultInterpreterPath"


class VSCode:
    def __init__(self, root: Path, code: Optional[str] = shutil.which("code")) -> None:
        self.root = root
        self.code = code
        self.workspace_settings = self.root.joinpath(".vscode/settings.json")

    def __repr__(self) -> str:
        return self.__class__.__qualname__ + f"(root={self.root!r}, code={self.code!r})"

    def raise_for_code(self) -> None:
        if not self.code:
            raise CodeNotInstalledError(
                "VSCode binary application `code` not found on $PATH."
            )

    def open(self) -> None:
        """
        Opens a project root in VSCode using the
        `code` CLI command.
        """

        self.raise_for_code()

        try:
            # Use the code binary to open the project
            subprocess.run([f"{self.code}", f"{self.root}"], check=True)
        except subprocess.CalledProcessError:
            raise

    def set_workspace_python(self, python_path: Path) -> None:
        """
        Sets the VSCode workspace setting `python.pythonPath`
        to `python_path`, overwriting if already exists.

        Take care not to resolve `python_path` as it will
        resolve the symlink back to the system python. As such,
        `python_path` should be the executable from a `VirtualEnv`
        or `CondaEnv` class to ensure this is safely done.

        Args:
            python_path (pathlib.Path): The path of the
                virtual environments python interpreter.
        """

        new_settings_dict: Dict[str, str] = {WORKSPACE_PYTHON_SETTING: str(python_path)}

        if not self.workspace_settings.exists():
            self.workspace_settings.parent.mkdir(parents=True)
            self.workspace_settings.touch()

        if len(self.workspace_settings.read_text()) == 0:
            # The file is empty, we don't have to worry about
            # preserving it's contents
            with open(self.workspace_settings, mode="w", encoding="utf-8") as f:
                json.dump(new_settings_dict, f, sort_keys=True, indent=4)
        else:
            # File exists and is not empty, let's preserve whatever
            # settings are already here
            with open(self.workspace_settings, mode="r", encoding="utf-8") as f:
                settings: Dict[str, Any] = json.load(f)

            # Wipe the file and recreate it so it's now empty
            self.workspace_settings.unlink()
            self.workspace_settings.touch()

            # Update the settings with our new python path
            settings.update(new_settings_dict)

            # Write the new settings back
            with open(self.workspace_settings, mode="w", encoding="utf-8") as f:
                json.dump(settings, f, sort_keys=True, indent=4)
