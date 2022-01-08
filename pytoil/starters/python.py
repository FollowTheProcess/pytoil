"""
The python starter template.


Author: Tom Fleet
Created: 29/12/2021
"""


from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import aiofiles
import aiofiles.os


@dataclass
class PythonStarter:
    path: Path
    name: str

    def __post_init__(self) -> None:
        self.root = self.path.joinpath(self.name).resolve()
        self.files: list[Path] = [
            self.root.joinpath(filename)
            for filename in ["README.md", "requirements.txt", f"{self.name}.py"]
        ]

    async def generate(self, username: str | None = None) -> None:
        """
        Generate a new python starter template.
        """
        await aiofiles.os.mkdir(self.root)

        for file in self.files:
            file.touch()

        # Put the header in the README
        readme = self.root.joinpath("README.md")
        async with aiofiles.open(readme, mode="w", encoding="utf-8") as f:
            await f.write(f"# {self.name}\n")

        # Put a hint in the requirements.txt
        reqs = self.root.joinpath("requirements.txt")
        async with aiofiles.open(reqs, mode="w", encoding="utf-8") as f:
            await f.write("# Put your requirements here e.g. flask>=1.0.0\n")

        # Populate the python file
        py_file = self.root.joinpath(f"{self.name}.py")
        py_text = (
            'def hello(name: str = "world") -> None:\n    print(f"hello {name}")\n'
        )
        async with aiofiles.open(py_file, mode="w", encoding="utf-8") as f:
            await f.write(py_text)
