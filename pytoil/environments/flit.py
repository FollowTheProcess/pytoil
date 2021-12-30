"""
Module responsible for handling Flit python environments.


Author: Tom Fleet
Created: 26/12/2021
"""

import asyncio
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from pytoil.environments.virtualenv import Venv
from pytoil.exceptions import FlitNotInstalledError


@dataclass
class Flit(Venv):
    """
    Representation of a Flit python environment.

    Subclasses `Venv` as a lot of shared functionality.
    """

    root: Path
    flit: Optional[str] = shutil.which("flit")

    @property
    def name(self) -> str:
        return "flit"

    async def install_self(self, silent: bool = False) -> None:
        """
        Installs a flit based project.

        Args:
            silent (bool, optional): Whether to discard or display output.
                Defaults to False.
        """
        if not self.flit:
            raise FlitNotInstalledError

        # Unlike poetry, conda etc. flit does not make it's own virtual environment
        # we must make one here before installing the project
        if not await self.exists():
            await self.create()

        proc = await asyncio.create_subprocess_exec(
            self.flit,
            "install",
            "--deps",
            "develop",
            "--symlink",
            "--python",
            f"{self.executable}",
            cwd=self.project_path,
            stdout=asyncio.subprocess.DEVNULL if silent else sys.stdout,
            stderr=asyncio.subprocess.DEVNULL if silent else sys.stderr,
        )

        await proc.wait()
