"""
Module responsible for handling python environments
with a `requirements.txt` (or `requirements-dev.txt`)


Author: Tom Fleet
Created: 26/12/2021
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import aiofiles.os

from pytoil.environments.virtualenv import Venv


class Requirements(Venv):
    def __init__(self, root: Path) -> None:
        self.root = root
        super().__init__(root)

    def __repr__(self) -> str:
        return self.__class__.__qualname__ + f"(root={self.root!r})"

    __slots__ = ("root",)

    @property
    def name(self) -> str:
        return "requirements file"

    async def install_self(self, silent: bool = False) -> None:
        """
        Installs everything in the requirements file into
        a python environment.
        """
        if not await self.exists():
            await self.create(silent=silent)

        requirements_file = "requirements.txt"

        if await aiofiles.os.path.exists(
            self.project_path.joinpath("requirements-dev.txt")
        ):
            requirements_file = "requirements-dev.txt"

        proc = await asyncio.create_subprocess_exec(
            f"{self.executable}",
            "-m",
            "pip",
            "install",
            "-r",
            requirements_file,
            cwd=self.project_path,
            stdout=asyncio.subprocess.DEVNULL if silent else sys.stdout,
            stderr=asyncio.subprocess.DEVNULL if silent else sys.stderr,
        )

        await proc.wait()
