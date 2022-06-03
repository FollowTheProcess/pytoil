"""
The rust starter template.


Author: Tom Fleet
Created: 29/12/2021
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from pytoil.exceptions import CargoNotInstalledError

CARGO = shutil.which("cargo")


class RustStarter:
    def __init__(self, path: Path, name: str, cargo: str | None = CARGO) -> None:
        self.path = path
        self.name = name
        self.cargo = cargo
        self.root = self.path.joinpath(self.name).resolve()
        self.files = [self.root.joinpath(filename) for filename in ["README.md"]]

    def __repr__(self) -> str:
        return (
            self.__class__.__qualname__
            + f"(path={self.path!r}, name={self.name!r}, cargo={self.cargo!r})"
        )

    __slots__ = ("path", "name", "cargo", "root", "files")

    def generate(self, username: str | None = None) -> None:
        """
        Generate a new rust/cargo starter template.
        """
        if not self.cargo:
            raise CargoNotInstalledError

        self.root.mkdir()

        # Call cargo init
        subprocess.run(
            [self.cargo, "init", "--vcs", "none"],
            cwd=self.root,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )

        # Create the README
        for file in self.files:
            file.touch()

        readme = self.root.joinpath("README.md")
        with open(readme, mode="w", encoding="utf-8") as f:
            f.write(f"# {self.name}\n")
