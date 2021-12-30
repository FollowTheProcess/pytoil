"""
Module responsible for handling python virtual environments
through the std lib `venv` module.


Author: Tom Fleet
Created: 24/12/2021
"""

import asyncio
import functools
import sys
import venv
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence

import aiofiles.os

from pytoil.exceptions import MissingInterpreterError


@dataclass
class Venv:
    root: Path

    @property
    def project_path(self) -> Path:
        return self.root.resolve()

    @property
    def executable(self) -> Path:
        return self.project_path.joinpath(".venv/bin/python")

    @property
    def name(self) -> str:
        return "venv"

    async def exists(self) -> bool:
        """
        Checks whether the virtual environment exists by a proxy
        check if the `executable` exists.

        If this executable exists then both the project and virtual environment
        must also exist and therefore must be valid.
        """
        # types-aiofiles hasn't caught up yet
        return await aiofiles.os.path.exists(self.executable)  # type: ignore

    async def create(
        self, packages: Optional[Sequence[str]] = None, silent: bool = False
    ) -> None:
        """
        Create the virtual environment in the project.

        If packages are specified here, these will be installed
        once the environment is created.

        Args:
            packages (Optional[List[str]], optional): Packages to install immediately
                after environment creation. Defaults to None.
            silent (bool, optional): Whether to discard or display output.
                Defaults to False.
        """
        # `clear` will ensure any existing venv is destroyed first rather
        # than causing an error
        # TODO: `create()` has an `upgrade_deps` arg to do what `update_seeds` does but
        # it's only in python 3.9
        # Add this in later

        # venv create is blocking and does not take kwargs
        # it is also silent by default
        # TODO: I'm actually not sure how to mock this out?
        # maybe we just create a tempdir and create a real venv, check the contents
        # then delete it? Would slow down the tests though
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            executor=None,
            func=functools.partial(
                venv.create,
                env_dir=self.project_path.joinpath(".venv"),
                clear=True,
                with_pip=True,
            ),
        )

        # Update core deps
        await self.update_seeds(silent=silent)

        # Install any specified packages
        if packages:
            await self.install(packages=packages, silent=silent)

    async def update_seeds(self, silent: bool = False) -> None:
        """
        Venv will install so-called "seed" packages to a new environment:
        `pip`, `setuptools` and `wheel`.

        It is good practice to keep these packages up to date, which this
        method does by invoking `pip` from the virtualenvs executable.

        This is equivalent to running:
        `python -m pip install --upgrade pip setuptools wheel`
        from the command line with the virtualenv activated.
        """
        if not await self.exists():
            raise MissingInterpreterError(f"Interpreter: {self.executable} not found.")

        proc = await asyncio.create_subprocess_exec(
            f"{self.executable}",
            "-m",
            "pip",
            "install",
            "--upgrade",
            "pip",
            "setuptools",
            "wheel",
            cwd=self.project_path,
            stdout=asyncio.subprocess.DEVNULL if silent else sys.stdout,
            stderr=asyncio.subprocess.DEVNULL if silent else sys.stderr,
        )

        await proc.wait()

    async def install(self, packages: Sequence[str], silent: bool = False) -> None:
        """
        Generic `pip install` method.

        Takes a list of packages to install. All packages are passed through to pip
        so any versioning syntax will work as expected.

        Args:
            packages (List[str]): List of packages to install, if only 1 package
                still must be a list e.g. `["black"]`.
            silent (bool, optional): Whether to discard or display output.
                Defaults to False.
        """
        proc = await asyncio.create_subprocess_exec(
            f"{self.executable}",
            "-m",
            "pip",
            "install",
            *packages,
            cwd=self.project_path,
            stdout=asyncio.subprocess.DEVNULL if silent else sys.stdout,
            stderr=asyncio.subprocess.DEVNULL if silent else sys.stderr,
        )

        await proc.wait()

    async def install_self(self, silent: bool = False) -> None:
        """
        Installs current package.

        We first try the equivalent of `pip install -e .[dev]` as a large
        number of packages declare a [dev] extra which contains everything
        needed to work on it.

        Pip will automatically fall back to `pip install -e .` in the event
        `.[dev]` does not exist and every python package must know how to
        install itself this way by definition.

        Args:
            silent (bool, optional): Whether to discard or display output.
                Defaults to False.
        """
        # Before installing the package, ensure a virtualenv exists
        if not await self.exists():
            await self.create(silent=silent)

        # We try .[dev] first as most packages I've seen have this
        # and pip will automatically fall back to '.' if not
        proc = await asyncio.create_subprocess_exec(
            f"{self.executable}",
            "-m",
            "pip",
            "install",
            "-e",
            ".[dev]",
            cwd=self.project_path,
            stdout=asyncio.subprocess.DEVNULL if silent else sys.stdout,
            stderr=asyncio.subprocess.DEVNULL if silent else sys.stderr,
        )

        await proc.wait()
