"""
The python starter template.

Author: Tom Fleet
Created: 23/06/2021
"""

from pathlib import Path
from typing import List, Optional

from pytoil.starters.base import BaseStarter


class PythonStarter(BaseStarter):
    def __init__(self, path: Path, name: str) -> None:
        """
        The pytoil python starter template.

        Args:
            path (Path): Root path under which to generate the
                project from this template.
            name (str): The name of the project to be created.
        """
        self._path = path
        self._name = name
        self._files: List[str] = ["README.md", "requirements.txt", f"{self.name}.py"]

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

    def generate(self, username: Optional[str] = None) -> None:
        """
        Generate a new python starter template.

        Because this is a python starter, we can just
        create all the files directly.
        """
        # Make the parent directory
        self.root.mkdir(parents=True)

        for file in self.files:
            file.touch()

        # Put the header in the readme
        readme = self.root.joinpath("README.md")
        readme.write_text(f"# {self.name}\n", encoding="utf-8")

        # Put a hint in the requirements.txt
        reqs = self.root.joinpath("requirements.txt")
        reqs.write_text(
            "# Put your requirements here e.g. flask>=1.0.0\n", encoding="utf-8"
        )

        # Populate the python file
        py_file = self.root.joinpath(f"{self.name}.py")
        py_text = (
            'def hello(name: str = "world") -> None:\n    print(f"hello {name}")\n'
        )
        py_file.write_text(py_text, encoding="utf-8")
