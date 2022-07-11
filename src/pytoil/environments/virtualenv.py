"""
Module responsible for handling python virtual environments
through the std lib `venv` module.


Author: Tom Fleet
Created: 24/12/2021
"""

from __future__ import annotations

import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

import virtualenv


class Venv:
    root: Path

    def __init__(self, root: Path) -> None:
        self.root = root

    def __repr__(self) -> str:
        return self.__class__.__qualname__ + f"(root={self.root!r})"

    __slots__ = ("root",)

    @property
    def project_path(self) -> Path:
        return self.root.resolve()

    @property
    def executable(self) -> Path:
        return self.project_path.joinpath(".venv/bin/python")

    @property
    def name(self) -> str:
        return "venv"

    def exists(self) -> bool:
        """
        Checks whether the virtual environment exists by a proxy
        check if the `executable` exists.

        If this executable exists then both the project and virtual environment
        must also exist and therefore must be valid.
        """
        return self.executable.exists()

    def create(
        self, packages: Sequence[str] | None = None, silent: bool = False
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
        virtualenv.cli_run(args=[str(self.project_path.joinpath(".venv")), "--quiet"])

        # Install any specified packages
        if packages:  # pragma: no cover
            self.install(packages=packages, silent=silent)

    def install(self, packages: Sequence[str], silent: bool = False) -> None:
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
        subprocess.run(
            [f"{self.executable}", "-m", "pip", "install", *packages],
            cwd=self.project_path,
            stdout=subprocess.DEVNULL if silent else sys.stdout,
            stderr=subprocess.DEVNULL if silent else sys.stderr,
        )

    def install_self(self, silent: bool = False) -> None:
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
        if not self.exists():
            self.create(silent=silent)

        # We try .[dev] first as most packages I've seen have this
        # and pip will automatically fall back to '.' if not
        subprocess.run(
            [f"{self.executable}", "-m", "pip", "install", "-e", ".[dev]"],
            cwd=self.project_path,
            stdout=subprocess.DEVNULL if silent else sys.stdout,
            stderr=subprocess.DEVNULL if silent else sys.stderr,
        )
