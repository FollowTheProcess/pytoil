"""
Module responsible for handling Flit python environments.


Author: Tom Fleet
Created: 26/12/2021
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from pytoil.environments.virtualenv import Venv
from pytoil.exceptions import FlitNotInstalledError

FLIT = shutil.which("flit")


class Flit(Venv):
    def __init__(self, root: Path, flit: str | None = FLIT) -> None:
        self.root = root
        self.flit = flit
        super().__init__(root)

    def __repr__(self) -> str:
        return self.__class__.__qualname__ + f"(root={self.root!r}, flit={self.flit!r})"

    __slots__ = ("root", "flit")

    @property
    def name(self) -> str:
        return "flit"

    def install_self(self, silent: bool = False) -> None:
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
        if not self.exists():
            self.create()

        subprocess.run(
            [
                self.flit,
                "install",
                "--deps",
                "develop",
                "--symlink",
                "--python",
                f"{self.executable}",
            ],
            cwd=self.project_path,
            stdout=subprocess.DEVNULL if silent else sys.stdout,
            stderr=subprocess.DEVNULL if silent else sys.stderr,
        )
