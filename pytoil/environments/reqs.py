"""
Module responsible for handling python environments
with a `requirements.txt` (or `requirements_dev.txt`)


Author: Tom Fleet
Created: 26/12/2021
"""

import asyncio
import sys
from dataclasses import dataclass
from pathlib import Path

import aiofiles.os

from pytoil.environments.virtualenv import Venv


@dataclass
class Requirements(Venv):
    """
    Representation of a python environment from a requirements file.

    Subclasses `Venv` as a lot of the operations are identical.
    """

    root: Path

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

        if await aiofiles.os.path.exists(self.project_path.joinpath("requirements_dev.txt")):  # type: ignore
            requirements_file = "requirements_dev.txt"

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
