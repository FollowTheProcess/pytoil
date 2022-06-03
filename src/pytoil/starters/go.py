"""
The Go starter template.


Author: Tom Fleet
Created: 29/12/2021
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from pytoil.exceptions import GoNotInstalledError

GO = shutil.which("go")


class GoStarter:
    def __init__(self, path: Path, name: str, go: str | None = GO) -> None:
        self.path = path
        self.name = name
        self.go = go
        self.root = self.path.joinpath(self.name).resolve()
        self.files = [
            self.root.joinpath(filename) for filename in ["README.md", "main.go"]
        ]

    def __repr__(self) -> str:
        return (
            self.__class__.__qualname__
            + f"(path={self.path!r}, name={self.name!r}, go={self.go!r})"
        )

    __slots__ = ("path", "name", "go", "root", "files")

    def generate(self, username: str | None = None) -> None:
        """
        Generate a new Go starter template.
        """
        if not self.go:
            raise GoNotInstalledError

        self.root.mkdir()

        # Call go mod init
        subprocess.run(
            [self.go, "mod", "init", f"github.com/{username}/{self.name}"],
            cwd=self.root,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )

        for file in self.files:
            file.touch()

        # Put the header in the README
        readme = self.root.joinpath("README.md")
        with open(readme, mode="w", encoding="utf-8") as f:
            f.write(f"# {self.name}\n")

        # Populate the go file
        main_go = self.root.joinpath("main.go")
        with open(main_go, mode="w", encoding="utf-8") as f:
            f.write(
                'package main\n\nimport "fmt"\n\nfunc main() {\n\tfmt.Println("Hello'
                ' World")\n}\n'
            )
