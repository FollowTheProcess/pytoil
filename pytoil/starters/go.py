"""
The go starter template.

Author: Tom Fleet
Created: 24/06/2021
"""


import shutil
import subprocess
from pathlib import Path
from typing import List, Optional

from pytoil.exceptions import GoNotInstalledError
from pytoil.starters.base import BaseStarter


class GoStarter(BaseStarter):
    def __init__(self, path: Path, name: str) -> None:
        """
        The pytoil go starter template.

        Args:
            path (Path): Root path under which to generate the
                project from this template.
            name (str): The name of the project to be created.
        """
        self._path = path
        self._name = name
        self._files = ["README.md", "main.go"]

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

    def raise_for_go(self) -> None:
        if not bool(shutil.which("go")):
            raise GoNotInstalledError("Go not found on $PATH.")

    def generate(self, username: Optional[str] = None) -> None:
        """
        Generate a new go starter template.

        This is a mix of creating files in python, and invoking
        `go mod init` in a subprocess to initialise the go
        modules file.
        """

        # Must have go installed to run go mod init
        self.raise_for_go()

        # Make the parent directory
        self.root.mkdir(parents=True)

        for file in self.files:
            file.touch()

        # Put the header in the readme
        readme = self.root.joinpath("README.md")
        readme.write_text(f"# {self.name}\n", encoding="utf-8")

        # Populate the main.go file
        go_file = self.root.joinpath("main.go")
        go_text = 'package main\n\nimport "fmt"\n\nfunc main() {\n\tfmt.Println("Hello World")\n}\n'  # noqa: E501

        go_file.write_text(go_text, encoding="utf-8")

        # Invoke go mod init
        _ = subprocess.run(
            ["go", "mod", "init", f"github.com/{username}/{self.name}"],
            check=True,
            cwd=self.root,
            capture_output=True,
        )
