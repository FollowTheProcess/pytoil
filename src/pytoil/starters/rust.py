"""
The rust starter template.


Author: Tom Fleet
Created: 29/12/2021
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from typing import TYPE_CHECKING

from pytoil.exceptions import CargoNotInstalledError

if TYPE_CHECKING:
    from pathlib import Path

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
        _ = username  # not needed for rust
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
        readme.write_text(f"# {self.name}\n", encoding="utf-8")
