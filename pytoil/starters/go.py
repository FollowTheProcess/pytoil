"""
The Go starter template.


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

from pytoil.exceptions import GoNotInstalledError


@dataclass
class GoStarter:
    path: Path
    name: str
    go: Optional[str] = shutil.which("go")

    def __post_init__(self) -> None:
        self.root = self.path.joinpath(self.name).resolve()
        self.files: List[Path] = [
            self.root.joinpath(filename) for filename in ["README.md", "main.go"]
        ]

    async def generate(self, username: Optional[str] = None) -> None:
        """
        Generate a new Go starter template.
        """
        if not self.go:
            raise GoNotInstalledError

        await aiofiles.os.mkdir(self.root)

        # Call go mod init
        proc = await asyncio.create_subprocess_exec(
            self.go,
            "mod",
            "init",
            f"github.com/{username}/{self.name}",
            cwd=self.root,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )

        await proc.wait()

        for file in self.files:
            file.touch()

        # Put the header in the README
        readme = self.root.joinpath("README.md")
        async with aiofiles.open(readme, mode="w", encoding="utf-8") as f:
            await f.write(f"# {self.name}\n")

        # Populate the go file
        main_go = self.root.joinpath("main.go")
        async with aiofiles.open(main_go, mode="w", encoding="utf-8") as f:
            await f.write(
                'package main\n\nimport "fmt"\n\nfunc main() {\n\tfmt.Println("Hello'
                ' World")\n}\n'
            )
