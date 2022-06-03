"""
Module responsible for handling python environments
with a `requirements.txt` (or `requirements-dev.txt`)


Author: Tom Fleet
Created: 26/12/2021
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

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

    def install_self(self, silent: bool = False) -> None:
        """
        Installs everything in the requirements file into
        a python environment.
        """
        if not self.exists():
            self.create(silent=silent)

        requirements_file = "requirements.txt"

        if self.project_path.joinpath("requirements-dev.txt").exists():
            requirements_file = "requirements-dev.txt"

        subprocess.run(
            [f"{self.executable}", "-m", "pip", "install", "-r", requirements_file],
            cwd=self.project_path,
            stdout=subprocess.DEVNULL if silent else sys.stdout,
            stderr=subprocess.DEVNULL if silent else sys.stderr,
        )
