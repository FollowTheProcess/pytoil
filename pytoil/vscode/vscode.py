"""
Module responsible for pytoil's interface with VSCode.


Author: Tom Fleet
Created: 23/12/2021
"""

from __future__ import annotations

import asyncio
import json
import shutil
import sys
from pathlib import Path

import aiofiles
import aiofiles.os

from pytoil.exceptions import CodeNotInstalledError

# From VSCode 1.57.1 the 'python.pythonPath' setting is being
# deprecated in favour of 'python.defaultInterpreterPath'
# it works in a slightly different way but for us it's effectively
# a straight swap
WORKSPACE_PYTHON_SETTING = "python.defaultInterpreterPath"

CODE = shutil.which("code")


class VSCode:
    def __init__(self, root: Path, code: str | None = CODE) -> None:
        self.root = root
        self.code = code

    def __repr__(self) -> str:
        return self.__class__.__qualname__ + f"(root={self.root!r}, code={self.code!r})"

    __slots__ = ("root", "code")

    @property
    def workspace_settings(self) -> Path:
        """
        Return the absolute path to the project's root
        VSCode workspace settings file.
        """
        return self.root.joinpath(".vscode/settings.json")

    async def open(self) -> None:
        """
        Opens a project root in VSCode using the configured
        code binary command.
        """
        if not self.code:
            raise CodeNotInstalledError

        proc = await asyncio.create_subprocess_exec(
            self.code,
            ".",
            cwd=self.root,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )

        await proc.wait()

    async def set_workspace_python(self, python_path: Path) -> None:
        """
        Sets the VSCode workspace setting `python.defaultInterpreterPath`
        to `python_path`, overwriting if already exists.

        Args:
            python_path (Path): The path to the virtual environment's
                python interpreter.
        """
        # Take care not to resolve `python_path` as it will resolve the symlink
        # back to the system python. As such, `python_path` should be the executable
        # from a `VirtualEnv` or a `CondaEnv` class to ensure this is safely done

        new_settings_dict: dict[str, str] = {WORKSPACE_PYTHON_SETTING: str(python_path)}

        # 2 cases to worry about here:
        # 1) File doesn't exist -> easy, just write new ones
        # 2) File exists -> read in what is already there, add new settings, write back overwriting

        if not await aiofiles.os.path.exists(self.workspace_settings):
            # Create and write new ones
            # The entire .vscode folder might not exist
            await aiofiles.os.makedirs(self.workspace_settings.parent, exist_ok=True)
            async with aiofiles.open(
                self.workspace_settings, mode="w", encoding="utf-8"
            ) as file:
                content = json.dumps(new_settings_dict)
                await file.write(content)

        else:
            # File exists, preserve any content
            async with aiofiles.open(
                self.workspace_settings, mode="r", encoding="utf-8"
            ) as file:
                content = await file.read()
                settings: dict[str, str] = json.loads(content)

            settings.update(new_settings_dict)

            # Write the new settings back
            async with aiofiles.open(
                self.workspace_settings, mode="w", encoding="utf-8"
            ) as file:
                content = json.dumps(settings)
                await file.write(content)
