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

        workspace_settings = self.root.joinpath(".vscode/settings.json")

        # settings.json may not exist yet, so create it explicitly
        workspace_settings.parent.mkdir(parents=True, exist_ok=True)
        workspace_settings.touch(exist_ok=True)

        new_settings_dict: Dict[str, str] = {"python.pythonPath": f"{python_path}"}

        with open(workspace_settings, "r+", encoding="utf-8") as f:
            workspace_settings_dict: Dict[str, Any] = json.load(f)
            workspace_settings_dict.update(new_settings_dict)
            json.dump(workspace_settings_dict, f)
