"""
Module responsible for handling poetry environments.

Here we take advantage of poetry's new `local` config setting
to enforce the virtual environment being in the project without
altering the user's base config.


Author: Tom Fleet
Created: 24/12/2021
"""

import asyncio
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence

import aiofiles.os

from pytoil.exceptions import PoetryNotInstalledError


@dataclass
class Poetry:
    root: Path
    poetry: Optional[str] = shutil.which("poetry")

    @property
    def project_path(self) -> Path:
        return self.root.resolve()

    @property
    def executable(self) -> Path:
        return self.project_path.joinpath(".venv/bin/python")

    @property
    def name(self) -> str:
        return "poetry"

    async def enforce_local_config(self, silent: bool = False) -> None:
        """
        Ensures any changes to poetry's config such as storing the
        virtual environment in the project directory as we do here, do not
        propegate to the user's global poetry config.
        """
        if not self.poetry:
            raise PoetryNotInstalledError

        proc = await asyncio.create_subprocess_exec(
            self.poetry,
            "config",
            "virtualenvs.in-project",
            "true",
            "--local",
            cwd=self.project_path,
            stdout=asyncio.subprocess.DEVNULL if silent else sys.stdout,
            stderr=asyncio.subprocess.DEVNULL if silent else sys.stderr,
        )

        await proc.wait()

    async def exists(self) -> bool:
        """
        Checks whether the virtual environment exists by a proxy
        check if the `executable` exists.

        If this executable exists then both the project and the virtual environment
        must also exist and must therefore be valid.
        """
        # types-aiofiles has not caught up yet
        return await aiofiles.os.path.exists(self.executable)  # type: ignore

    async def create(
        self, packages: Optional[Sequence[str]] = None, silent: bool = False
    ) -> None:
        """
        This method is not implemented for poetry environments.

        Use `install` instead as with poetry, creation and installation
        are handled together.
        """
        raise NotImplementedError

    async def install(self, packages: Sequence[str], silent: bool = False) -> None:
        """
        Calls `poetry add` to install packages into the environment.

        Args:
            packages (List[str]): List of packages to install.
            silent (bool, optional): Whether to discard or display output.
        """
        if not self.poetry:
            raise PoetryNotInstalledError

        await self.enforce_local_config()

        proc = await asyncio.create_subprocess_exec(
            self.poetry,
            "add",
            *packages,
            cwd=self.project_path,
            stdout=asyncio.subprocess.DEVNULL if silent else sys.stdout,
            stderr=asyncio.subprocess.DEVNULL if silent else sys.stderr,
        )

        await proc.wait()

    async def install_self(self, silent: bool = False) -> None:
        """
        Calls `poetry install` under the hood to install the current package
        and all it's dependencies.

        Args:
            silent (bool, optional): Whether to discard or display output.
                Defaults to False.
        """
        if not self.poetry:
            raise PoetryNotInstalledError

        await self.enforce_local_config()

        proc = await asyncio.create_subprocess_exec(
            self.poetry,
            "install",
            cwd=self.project_path,
            stdout=asyncio.subprocess.DEVNULL if silent else sys.stdout,
            stderr=asyncio.subprocess.DEVNULL if silent else sys.stderr,
        )

        await proc.wait()
