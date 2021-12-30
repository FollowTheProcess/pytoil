"""
The rust starter template.


Author: Tom Fleet
Created: 29/12/2021
"""

import asyncio
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import aiofiles
import aiofiles.os

from pytoil.exceptions import CargoNotInstalledError


@dataclass
class RustStarter:
    path: Path
    name: str
    cargo: Optional[str] = shutil.which("cargo")

    def __post_init__(self) -> None:
        self.root = self.path.joinpath(self.name).resolve()
        self.files: List[Path] = [
            self.root.joinpath(filename) for filename in ["README.md"]
        ]

    async def generate(self, username: Optional[str] = None) -> None:
        """
        Generate a new rust/cargo starter template.
        """
        if not self.cargo:
            raise CargoNotInstalledError

        await aiofiles.os.mkdir(self.root)

        # Call cargo init
        proc = await asyncio.create_subprocess_exec(
            self.cargo,
            "init",
            cwd=self.root,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )

        await proc.wait()

        # Create the README
        for file in self.files:
            file.touch()

        readme = self.root.joinpath("README.md")
        async with aiofiles.open(readme, mode="w", encoding="utf-8") as f:
            await f.write(f"# {self.name}\n")
