"""
The python starter template.


Author: Tom Fleet
Created: 29/12/2021
"""


from __future__ import annotations

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
        self.root.mkdir()

        for file in self.files:
            file.touch()

        # Put the header in the README
        readme = self.root.joinpath("README.md")
        with open(readme, mode="w", encoding="utf-8") as f:
            f.write(f"# {self.name}\n")

        # Put a hint in the requirements.txt
        reqs = self.root.joinpath("requirements.txt")
        with open(reqs, mode="w", encoding="utf-8") as f:
            f.write("# Put your requirements here e.g. flask>=1.0.0\n")

        # Populate the python file
        py_file = self.root.joinpath(f"{self.name}.py")
        py_text = (
            'def hello(name: str = "world") -> None:\n    print(f"hello {name}")\n'
        )
        with open(py_file, mode="w", encoding="utf-8") as f:
            f.write(py_text)
