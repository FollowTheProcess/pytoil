"""
Module responsible for handling launching a directory-aware editor
when opening a project.


Author: Tom Fleet
Created: 12/03/2022
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path


async def launch(path: Path, bin: str) -> None:
    """
    Launch a directory-aware editor from the command line binary
    `bin` to open a project with root at `path`.

    Launch assumes that the command to open a project is of the
    structure `<bin> <path>` e.g. `code ~/myproject`.

    Args:
        path (Path): Absolute path to the root of the project to open.
        bin (str): Name of the editor binary e.g. `code`.
    """
    proc = await asyncio.create_subprocess_exec(
        bin,
        path,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )

    await proc.wait()
