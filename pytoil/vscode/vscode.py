"""
Module responsible for opening vscode at the root
of a project and configuring it's settings.

e.g. setting `python.pythonPath` to match the
project's virtual environment.

Author: Tom Fleet
Created: 06/03/2021
"""

import json
import pathlib
import shutil
import subprocess
from typing import Any, Dict

from pytoil.exceptions import CodeNotInstalledError


class VSCode:
    def __init__(self, root: pathlib.Path) -> None:
        """
        Representation of VSCode.

        Used as a container for methods that open a target
        project or configure workspace settings.

        Args:
            root (pathlib.Path): Path of the project root.
        """

        self.root = root.resolve()

    def __repr__(self) -> str:
        return self.__class__.__qualname__ + f"(root={self.root!r})"

    def raise_if_not_installed(self) -> None:
        if not bool(shutil.which("code")):
            raise CodeNotInstalledError(
                """VSCode `code` binary not found on $PATH.
        Check your installation."""
            )

    def open(self) -> None:
        """
        Opens a project root in VSCode using
        the code CLI command.
        """

        self.raise_if_not_installed()

        try:
            # Use the code binary to open the project
            subprocess.run(["code", f"{self.root}"], check=True)
        except subprocess.CalledProcessError:
            raise

    def set_python_path(self, python_path: pathlib.Path) -> None:
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

        new_settings_dict: Dict[str, str] = {"python.pythonPath": str(python_path)}

        workspace_settings = self.root.joinpath(".vscode/settings.json")

        if not workspace_settings.exists():
            workspace_settings.parent.mkdir(parents=True)
            workspace_settings.touch()

        if len(workspace_settings.read_text()) == 0:
            # The file is empty, we don't have to worry about
            # preserving it's contents
            with open(workspace_settings, mode="w", encoding="utf-8") as f:
                json.dump(new_settings_dict, f, sort_keys=True, indent=4)
        else:
            # File exists and is not empty, let's preserve whatever
            # settings are already here
            with open(workspace_settings, mode="r", encoding="utf-8") as f:
                settings: Dict[str, Any] = json.load(f)

            # Wipe the file and recreate it so it's now empty
            workspace_settings.unlink()
            workspace_settings.touch()

            # Update the settings with our new python path
            settings.update(new_settings_dict)

            # Write the new settings back
            with open(workspace_settings, mode="w", encoding="utf-8") as f:
                json.dump(settings, f, sort_keys=True, indent=4)
