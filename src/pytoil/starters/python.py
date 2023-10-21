"""
The python starter template.


Author: Tom Fleet
Created: 29/12/2021
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


class PythonStarter:
    def __init__(self, path: Path, name: str) -> None:
        self.path = path
        self.name = name
        self.root = self.path.joinpath(self.name).resolve()
        self.files = [
            self.root.joinpath(filename)
            for filename in ["README.md", "requirements.txt", f"{self.name}.py"]
        ]

    def __repr__(self) -> str:
        return self.__class__.__qualname__ + f"(path={self.path!r}, name={self.name!r})"

    __slots__ = ("path", "name", "root", "files")

    def generate(self, username: str | None = None) -> None:
        """
        Generate a new python starter template.
        """
        _ = username  # not needed for python
        self.root.mkdir()

        for file in self.files:
            file.touch()

        # Put the header in the README
        readme = self.root.joinpath("README.md")
        reqs = self.root.joinpath("requirements.txt")
        py_file = self.root.joinpath(f"{self.name}.py")

        # Populate the python file
        py_text = (
            'def hello(name: str = "world") -> None:\n    print(f"hello {name}")\n'
        )

        readme.write_text(f"# {self.name}\n", encoding="utf-8")
        reqs.write_text(
            "# Put your requirements here e.g. flask>=1.0.0\n", encoding="utf-8"
        )
        py_file.write_text(py_text, encoding="utf-8")
