"""
The rust starter template.

Author: Tom Fleet
Created: 24/06/2021
"""

import shutil
import subprocess
from pathlib import Path
from typing import List, Optional

from pytoil.exceptions import CargoNotInstalledError
from pytoil.starters.base import BaseStarter


class RustStarter(BaseStarter):
    def __init__(self, path: Path, name: str) -> None:
        """
        The pytoil rust starter template.

        Args:
            path (Path): Root path under which to generate the
                project from this template.
            name (str): The name of the project to be created.
        """
        self._path = path
        self._name = name
        self._files = ["README.md"]

    def __repr__(self) -> str:
        return self.__class__.__qualname__ + f"(path={self.path!r}, name={self.name!r})"

    @property
    def path(self) -> Path:
        return self._path

    @property
    def name(self) -> str:
        return self._name

    @property
    def root(self) -> Path:
        return self._path.joinpath(self._name)

    @property
    def files(self) -> List[Path]:
        return [self.root.joinpath(filename) for filename in self._files]

    def raise_for_cargo(self) -> None:
        if not bool(shutil.which("cargo")):
            raise CargoNotInstalledError("Cargo not found on $PATH.")

    def generate(self, username: Optional[str] = None) -> None:
        """
        Generate a new cargo/rust starter template.

        This is basically all cargo, the only additional
        thing we do here is add in a README.
        """

        # Must have cargo installed
        self.raise_for_cargo()

        # Make the root dir
        self.root.mkdir(parents=True)

        # Invoke cargo in a subprocess to generate the project
        _ = subprocess.run(
            ["cargo", "init"],
            check=True,
            capture_output=True,
            cwd=self.root,
        )

        # Add in the readme
        for file in self.files:
            file.touch()

        readme = self.root.joinpath("README.md")
        readme.write_text(f"# {self.name}\n", encoding="utf-8")
